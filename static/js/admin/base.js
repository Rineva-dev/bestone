
document.addEventListener("DOMContentLoaded", function () {
  const header = document.getElementById("main-header");
  const menuToggle = document.getElementById("menu-toggle");
  const mobileMenu = document.getElementById("mobile-menu");
  const backToTop = document.getElementById("bo-back-to-top");

  // ==========================================
  // MENU MOBILE
  // ==========================================

  function closeMobileMenu() {
    if (!menuToggle || !mobileMenu) return;

    mobileMenu.hidden = true;
    menuToggle.classList.remove("is-open");
    menuToggle.setAttribute("aria-expanded", "false");
    menuToggle.setAttribute("aria-label", "Buka menu navigasi");

    document.body.classList.remove("bo-menu-open");
  }

  function openMobileMenu() {
    if (!menuToggle || !mobileMenu) return;

    mobileMenu.hidden = false;
    menuToggle.classList.add("is-open");
    menuToggle.setAttribute("aria-expanded", "true");
    menuToggle.setAttribute("aria-label", "Tutup menu navigasi");

    document.body.classList.add("bo-menu-open");
  }

  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener("click", function () {
      const isOpen = menuToggle.getAttribute("aria-expanded") === "true";

      if (isOpen) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });

    // Tutup menu setelah pengguna memilih tautan.
    mobileMenu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeMobileMenu);
    });

    // Tutup jika pengguna menekan Escape.
    document.addEventListener("keydown", function (event) {
      if (
        event.key === "Escape" &&
        menuToggle.getAttribute("aria-expanded") === "true"
      ) {
        closeMobileMenu();
        menuToggle.focus();
      }
    });

    // Jika kembali ke tampilan desktop, tutup menu mobile.
    window.addEventListener("resize", function () {
      if (window.innerWidth > 850) {
        closeMobileMenu();
      }
    });

    // Tutup jika pengguna mengeklik di luar header.
    document.addEventListener("click", function (event) {
      if (
        menuToggle.getAttribute("aria-expanded") === "true" &&
        header &&
        !header.contains(event.target)
      ) {
        closeMobileMenu();
      }
    });
  }

  // ==========================================
  // HEADER SAAT SCROLL
  // ==========================================

  function updateScrollUI() {
    const scrollPosition = window.scrollY || window.pageYOffset;

    if (header) {
      header.classList.toggle(
        "bo-header-scrolled",
        scrollPosition > 20
      );
    }

    if (backToTop) {
      backToTop.classList.toggle(
        "is-visible",
        scrollPosition > 350
      );
    }
  }

  window.addEventListener("scroll", updateScrollUI, {
    passive: true
  });

  updateScrollUI();

  // ==========================================
  // NAVIGASI AKTIF
  // ==========================================

  const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";

  document.querySelectorAll("[data-nav-path]").forEach(function (link) {
    const navPath = link.dataset.navPath;

    if (!navPath) return;

    const normalizedNavPath = navPath.replace(/\/+$/, "") || "/";

    // Beranda hanya aktif pada halaman utama.
    // Halaman dengan subpath tidak dianggap sebagai Beranda.
    const isActive = normalizedNavPath === "/"
      ? currentPath === "/"
      : currentPath === normalizedNavPath ||
        currentPath.startsWith(normalizedNavPath + "/");

    link.classList.toggle("is-active", isActive);

    if (isActive) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });

  // ==========================================
  // KEMBALI KE ATAS
  // ==========================================

  if (backToTop) {
    backToTop.addEventListener("click", function () {
      window.scrollTo({
        top: 0,
        behavior: window.matchMedia(
          "(prefers-reduced-motion: reduce)"
        ).matches ? "auto" : "smooth"
      });
    });
  }

  
  // ==========================================
  // TOGGLE SIDEBAR ADMIN
  // ==========================================
  const sidebar = document.getElementById("sidebar");
  const tombolSidebar = document.getElementById("tombolSidebar");

  let sidebarOverlay = document.querySelector(".sidebar-overlay");

  if (sidebar && tombolSidebar) {
    // Buat overlay khusus untuk sidebar mobile.
    if (!sidebarOverlay) {
      sidebarOverlay = document.createElement("div");
      sidebarOverlay.className = "sidebar-overlay";
      sidebarOverlay.setAttribute("aria-hidden", "true");
      document.body.appendChild(sidebarOverlay);
    }

    function bukaSidebar() {
      sidebar.classList.add("buka");
      sidebarOverlay.classList.add("aktif");
      tombolSidebar.setAttribute("aria-expanded", "true");
      document.body.style.overflow = "hidden";
    }

    function tutupSidebar() {
      sidebar.classList.remove("buka");
      sidebarOverlay.classList.remove("aktif");
      tombolSidebar.setAttribute("aria-expanded", "false");
      document.body.style.overflow = "";
    }

    tombolSidebar.setAttribute("aria-controls", "sidebar");
    tombolSidebar.setAttribute("aria-expanded", "false");

    tombolSidebar.addEventListener("click", function () {
      if (sidebar.classList.contains("buka")) {
        tutupSidebar();
      } else {
        bukaSidebar();
      }
    });

    sidebarOverlay.addEventListener("click", tutupSidebar);

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && sidebar.classList.contains("buka")) {
        tutupSidebar();
        tombolSidebar.focus();
      }
    });

    sidebar.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        if (window.innerWidth <= 768) {
          tutupSidebar();
        }
      });
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 768) {
        tutupSidebar();
      }
    });
  }


  if (window.lucide) {
    lucide.createIcons();
  }
});
