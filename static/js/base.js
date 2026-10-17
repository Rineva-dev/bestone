
document.addEventListener('DOMContentLoaded', function () {
  const header = document.getElementById('main-header');

  // Efek header saat halaman di-scroll
  if (header) {
    const updateHeader = () => {
      header.classList.toggle('bo-header-scrolled', window.scrollY > 50);
    };

    updateHeader();
    window.addEventListener('scroll', updateHeader, { passive: true });
  }

  // Toggle menu mobile
  const menuToggle = document.getElementById('menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');

  if (menuToggle && mobileMenu) {
    function bukaMenu() {
      mobileMenu.hidden = false;
      menuToggle.classList.add('is-open');
      menuToggle.setAttribute('aria-expanded', 'true');
      menuToggle.setAttribute('aria-label', 'Tutup menu navigasi');
      document.body.classList.add('bo-menu-open');
    }

    function tutupMenu() {
      mobileMenu.hidden = true;
      menuToggle.classList.remove('is-open');
      menuToggle.setAttribute('aria-expanded', 'false');
      menuToggle.setAttribute('aria-label', 'Buka menu navigasi');
      document.body.classList.remove('bo-menu-open');
    }

    menuToggle.addEventListener('click', function () {
      if (mobileMenu.hidden) {
        bukaMenu();
      } else {
        tutupMenu();
      }
    });

    // Tutup menu setelah pengguna memilih tautan
    mobileMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', tutupMenu);
    });

    // Tutup menu dengan tombol Escape
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && !mobileMenu.hidden) {
        tutupMenu();
        menuToggle.focus();
      }
    });

    // Tutup menu jika ukuran layar kembali ke desktop
    window.addEventListener('resize', function () {
      if (window.innerWidth > 850 && !mobileMenu.hidden) {
        tutupMenu();
      }
    });
  }
});
