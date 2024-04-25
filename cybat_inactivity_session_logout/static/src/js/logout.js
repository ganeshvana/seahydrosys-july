odoo.define("cybat_inactivity_session_logout.inactivity_timeout", function (require) {
    "use strict";

    const rpc = require("web.rpc");
    const session = require("web.session");
    const localStorage = window.localStorage;
    let SESSION_TIMEOUT = 10 * 60 * 1000;
    let timeoutId;
    if (session.user_id) {
        rpc.query({
            model: "ir.config_parameter",
            method: "search_read",
            domain: [["key", "=", "inactivity_session_logout_time"]],
            fields: ["value"],
            limit: 1,
        }).then(function (result) {
            if (result.length > 0 && result[0].value) {
                SESSION_TIMEOUT = result[0].value * 1000;
            }
        });
    }
    function logout() {
        session.session_logout().then(function () {
            session.uid = undefined;
            session.username = undefined;
            console.log("Logout Successful");
            window.location.href = "/web/login";
        });
    }

    function resetTimer() {
        clearTimeout(timeoutId);
        if (session.user_id) {
            timeoutId = setTimeout(logout, SESSION_TIMEOUT);
        }
    }

    function handleUserInteraction() {
        resetTimer();
        if (session.user_id) {
            localStorage.setItem("userActive", Date.now());
        }
    }

    const userInteractionEvents = [
        "mousemove",
        "mousedown",
        "keydown",
        "scroll",
        "select",
        "onload",
        "touchstart",
        "touchmove",
    ];
    userInteractionEvents.forEach((event) => {
        document.addEventListener(event, handleUserInteraction);
    });

    document.addEventListener("visibilitychange", function () {
        if (!document.hidden) {
            handleUserInteraction();
        }
    });

    window.addEventListener("focus", handleUserInteraction);
    window.addEventListener("blur", handleUserInteraction);
    window.addEventListener("load", () => {
        handleUserInteraction();
    });

    window.addEventListener("storage", (event) => {
        if (event.key === "userActive") {
            resetTimer();
        }
    });

    resetTimer();

    return {resetTimer};
});
