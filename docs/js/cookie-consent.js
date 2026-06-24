/* Cookie Consent Banner + Conditional Google Analytics */

(function () {
  var STORAGE_KEY = "capcat_cookie_consent";
  var GA_ID = "G-8QZZGPHWQ9";

  function getConsent() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function setConsent(value) {
    try {
      localStorage.setItem(STORAGE_KEY, value);
    } catch (e) {
      /* storage unavailable */
    }
  }

  function loadGtag() {
    if (document.querySelector('script[src*="googletagmanager"]')) return;

    var script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID;
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag("js", new Date());
    gtag("config", GA_ID);
  }

  function showBanner() {
    var banner = document.createElement("div");
    banner.id = "cookie-consent-banner";
    banner.setAttribute("role", "dialog");
    banner.setAttribute("aria-label", "Cookie consent");

    banner.innerHTML =
      '<div class="cookie-consent-inner">' +
        '<p class="cookie-consent-text">' +
          "This site uses cookies for anonymous analytics. " +
          "No personal data is collected." +
        "</p>" +
        '<div class="cookie-consent-actions">' +
          '<button id="cookie-accept" class="cookie-btn cookie-btn-accept">Accept</button>' +
          '<button id="cookie-decline" class="cookie-btn cookie-btn-decline">Decline</button>' +
        "</div>" +
      "</div>";

    document.body.appendChild(banner);

    document.getElementById("cookie-accept").addEventListener("click", function () {
      setConsent("granted");
      loadGtag();
      removeBanner();
    });

    document.getElementById("cookie-decline").addEventListener("click", function () {
      setConsent("denied");
      removeBanner();
    });

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        banner.classList.add("cookie-consent-visible");
      });
    });
  }

  function removeBanner() {
    var banner = document.getElementById("cookie-consent-banner");
    if (!banner) return;
    banner.classList.remove("cookie-consent-visible");
    banner.addEventListener("transitionend", function () {
      banner.remove();
    });
  }

  /* Init */
  var consent = getConsent();
  if (consent === "granted") {
    loadGtag();
  } else if (consent === null) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", showBanner);
    } else {
      showBanner();
    }
  }
})();
