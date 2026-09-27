/* SKOM — minimal site script: mobile menu, program sub-menu, form handling,
   and fade-in-up entrance (Elementor "Motion Effects" equivalent). */
(function () {
  "use strict";
  var doc = document.documentElement;

  /* ---- Mobile menu ---- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  function setMenu(open) {
    doc.classList.toggle("nav-open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.querySelector(".nav-toggle-label").textContent = open ? "Close" : "Menu";
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      setMenu(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && doc.classList.contains("nav-open")) { setMenu(false); toggle.focus(); }
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setMenu(false);
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 1180 && doc.classList.contains("nav-open")) setMenu(false);
    });
  }

  /* ---- Programs sub-menu toggle (touch + keyboard) ---- */
  document.querySelectorAll(".sub-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.closest(".has-sub");
      var open = !li.classList.contains("open");
      li.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
    });
  });
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".has-sub.open").forEach(function (li) {
      if (!li.contains(e.target) && window.innerWidth > 1180) {
        li.classList.remove("open");
        li.querySelector(".sub-toggle").setAttribute("aria-expanded", "false");
      }
    });
  });

  /* ---- Pre-select enquiry type from ?type= (e.g. /contact/?type=partnership) ---- */
  var params = new URLSearchParams(window.location.search);
  var preset = params.get("type");
  if (preset) {
    var sel = document.querySelector('select[name="enquiry_type"], select[name="support_type"], select[name="partner_type"]');
    if (sel && sel.querySelector('option[value="' + CSS.escape(preset) + '"]')) sel.value = preset;
  }

  /* ---- Forms ---- */
  function fieldOf(el) { return el.closest(".field"); }
  function clearError(el) {
    var f = fieldOf(el); if (!f) return;
    f.classList.remove("invalid");
    el.removeAttribute("aria-invalid");
    var msg = f.querySelector(".field-error"); if (msg) msg.remove();
  }
  function showError(el, text) {
    var f = fieldOf(el); if (!f) return;
    clearError(el);
    f.classList.add("invalid");
    el.setAttribute("aria-invalid", "true");
    var msg = document.createElement("span");
    msg.className = "field-error";
    msg.id = el.id + "-error";
    msg.textContent = text;
    el.setAttribute("aria-describedby", msg.id);
    f.appendChild(msg);
  }
  function validate(el) {
    if (el.validity.valid) { clearError(el); return true; }
    if (el.validity.valueMissing) {
      showError(el, el.type === "checkbox" ? "Please tick this box to continue." :
        el.tagName === "SELECT" ? "Please choose an option." : "This field is required.");
    } else if (el.validity.typeMismatch && el.type === "email") {
      showError(el, "Please enter a valid email address, e.g. name@example.com.");
    } else {
      showError(el, "Please check this field.");
    }
    return false;
  }

  document.querySelectorAll(".skom-form").forEach(function (form) {
    var status = form.querySelector(".form-status");
    form.querySelectorAll("input, select, textarea").forEach(function (el) {
      el.addEventListener("blur", function () { if (el.required && (el.value || fieldOf(el).classList.contains("invalid"))) validate(el); });
      el.addEventListener("change", function () { if (fieldOf(el) && fieldOf(el).classList.contains("invalid")) validate(el); });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var firstBad = null;
      form.querySelectorAll("[required]").forEach(function (el) {
        if (!validate(el) && !firstBad) firstBad = el;
      });
      if (firstBad) { firstBad.focus(); return; }

      var endpoint = form.getAttribute("data-endpoint");
      var nameField = form.querySelector('[name="name"]');
      var who = nameField && nameField.value ? nameField.value.trim().split(" ")[0] : "";
      status.hidden = false;

      var mailto = form.getAttribute("data-mailto");
      if (!endpoint && mailto) {
        /* No form service yet: open the visitor's email app with the message pre-filled. */
        var lines = [];
        form.querySelectorAll("input, select, textarea").forEach(function (el) {
          if (el.type === "checkbox" && el.name !== "interest") return;
          if (el.type === "checkbox" && !el.checked) return;
          var v = el.tagName === "SELECT" ? el.options[el.selectedIndex].text : el.value;
          if (!v) return;
          var lab = el.labels && el.labels[0] ? el.labels[0].textContent.replace(/\*|\(optional\)/g, "").trim() : el.name;
          lines.push(lab + ": " + v);
        });
        var subject = "Website enquiry" + (who ? " from " + nameField.value.trim() : "");
        window.location.href = "mailto:" + mailto + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
        status.className = "form-status is-success";
        status.textContent = "Thank you" + (who ? ", " + who : "") + ". Your email app should now open with your message ready — just press send. If it doesn’t open, email SKOM directly at " + mailto + ".";
        return;
      }
      if (!endpoint) {
        /* No delivery service configured yet — be honest with the visitor. */
        status.className = "form-status is-pending";
        status.textContent = "Thank you" + (who ? ", " + who : "") +
          ". Online form delivery for SKOM is still being set up, so this message has not been sent yet. " +
          "Please keep a copy of your message — SKOM’s direct contact details will be published on this site shortly.";
        return;
      }

      var btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      status.className = "form-status";
      status.textContent = "Sending…";
      fetch(endpoint, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          status.className = "form-status is-success";
          status.textContent = "Thank you" + (who ? ", " + who : "") + ". Your message has been sent — SKOM will be in touch.";
          form.reset();
        })
        .catch(function () {
          status.className = "form-status is-error";
          status.textContent = "Sorry, something went wrong sending your message. Please try again in a moment.";
        })
        .finally(function () { btn.disabled = false; });
    });
  });

  /* ---- Footer year ---- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---- Entrance animation ---- */
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-visible"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("is-visible"); });
  }
})();
