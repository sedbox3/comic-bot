// ============================================
// Sedbox Comics - Internationalization (i18n)
// ============================================

const I18N = {
  // Supported languages
  supported: ['ar', 'en', 'tr', 'fr', 'es', 'pt', 'de', 'ja', 'ko', 'zh'],
  
  // RTL languages
  rtlLanguages: ['ar', 'he', 'fa', 'ur'],
  
  // Current language
  current: 'en',
  
  // Translations
  translations: {
    ar: {
      // Navigation
      home: 'الرئيسية',
      browse: 'تصفح',
      trending: 'الأكثر قراءة',
      latest: 'أحدث الإضافات',
      search: 'ابحث...',
      searchCtrlK: 'ابحث... (Ctrl+K)',
      signUp: 'تسجيل',
      login: 'تسجيل الدخول',
      logout: 'خروج',
      dashboard: 'لوحة التحكم',
      site: 'الموقع',
      
      // Hero
      heroBadge: '📚 أكبر مكتبة كوميكس عربية',
      heroTitle1: 'اكتشف عالماً من',
      heroTitle2: 'القصص المصورة',
      heroDesc: 'آلاف الكوميكس بجودة عالية، مجاناً وبدون إعلانات.',
      startReading: 'ابدأ القراءة',
      
      // Sections
      trendingComics: 'كوميكس رائجة',
      trendingNovels: 'روايات رائجة',
      latestUpdates: 'آخر التحديثات',
      browseAll: 'عرض الكل',
      viewAll: 'عرض الكل',
      
      // Comic Card
      readNow: 'اقرأ الآن',
      views: 'مشاهدات',
      chapters: 'فصول',
      pages: 'صفحات',
      rating: 'التقييم',
      
      // Categories
      allCategories: 'الكل',
      
      // Comic Detail
      synopsis: 'ملخص',
      by: 'بقلم',
      startReadingBtn: 'ابدأ القراءة',
      chaptersList: 'الفصول',
      noChapters: 'لا توجد فصول بعد',
      noDescription: 'لا يوجد وصف',
      
      // Reader
      prevChapter: 'الفصل السابق',
      nextChapter: 'الفصل التالي',
      page: 'صفحة',
      of: 'من',
      toggleMode: 'تغيير الوضع',
      zoomIn: 'تكبير',
      zoomOut: 'تصغير',
      close: 'إغلاق',
      noPages: 'لا توجد صور',
      loading: 'جاري التحميل...',
      
      // Browse
      browseAllComics: 'تصفح جميع الكوميكس',
      sortBy: 'ترتيب حسب:',
      latestFirst: 'الأحدث أولاً',
      mostPopular: 'الأكثر شعبية',
      highestRating: 'الأعلى تقييماً',
      az: 'أ - ي',
      gridView: 'شبكة',
      listView: 'قائمة',
      showing: 'عرض',
      results: 'نتائج',
      noResults: 'لم يتم العثور على نتائج',
      trySearch: 'جرب البحث بكلمات مختلفة',
      resetFilters: 'إعادة تعيين الفلاتر',
      
      // Admin Dashboard
      quickActions: 'إجراءات سريعة',
      addNewComic: 'إضافة كوميكس جديد',
      uploadChapters: 'رفع فصول',
      manageCategories: 'إدارة التصنيفات',
      systemInfo: 'معلومات النظام',
      platform: 'المنصة',
      version: 'الإصدار',
      backend: 'الخادم',
      hosting: 'الاستضافة',
      
      // Admin Comics
      manageComics: 'إدارة الكوميكس',
      addComic: 'إضافة كوميكس',
      title: 'العنوان',
      category: 'التصنيف',
      author: 'المؤلف',
      description: 'الوصف',
      coverImage: 'صورة الغلاف',
      clickOrDrag: 'انقر أو اسحب لرفع الصورة',
      saveComic: 'حفظ الكوميكس',
      cancel: 'إلغاء',
      selectCategory: 'اختر التصنيف',
      noComicsYet: 'لا يوجد كوميكس بعد',
      startByAdding: 'ابدأ بإضافة أول كوميكس',
      deleteComic: 'حذف',
      
      // Admin Chapters
      manageChapters: 'إدارة الفصول',
      addChapter: 'إضافة فصل',
      comic: 'الكوميكس',
      chapterNumber: 'رقم الفصل',
      chapterTitle: 'عنوان الفصل',
      pagesImages: 'صور الصفحات',
      clickOrDragImages: 'انقر أو اسحب الصور هنا',
      multipleFiles: 'يمكنك اختيار عدة ملفات',
      saveChapter: 'حفظ الفصل',
      selectComic: 'اختر الكوميكس',
      noChaptersYet: 'لا توجد فصول بعد',
      startByAddingChapter: 'ابدأ بإضافة أول فصل',
      
      // Admin Categories
      manageCategoriesTitle: 'إدارة التصنيفات',
      addCategory: 'إضافة تصنيف',
      categoryName: 'اسم التصنيف',
      add: 'إضافة',
      noCategoriesYet: 'لا توجد تصنيفات بعد',
      startByAddingCategory: 'ابدأ بإضافة أول تصنيف',
      
      // Admin Settings
      settings: 'الإعدادات',
      changePassword: 'تغيير كلمة المرور',
      currentPassword: 'كلمة المرور الحالية',
      newPassword: 'كلمة المرور الجديدة',
      confirmPassword: 'تأكيد كلمة المرور',
      saveChanges: 'حفظ التغييرات',
      exportData: 'تصدير البيانات',
      exportDesc: 'تصدير جميع البيانات كملف احتياطي JSON',
      exportJson: 'تصدير JSON',
      importData: 'استيراد البيانات',
      importDesc: 'استيراد بيانات من ملف JSON',
      dropJsonHere: 'اسحب ملف JSON هنا',
      dangerZone: 'منطقة الخطر',
      dangerDesc: 'حذف جميع البيانات نهائياً. لا يمكن التراجع.',
      deleteAllData: 'حذف كل البيانات',
      
      // Messages
      passwordMismatch: 'كلمتا المرور غير متطابقتين',
      currentPasswordIncorrect: 'كلمة المرور الحالية غير صحيحة',
      passwordChanged: 'تم تغيير كلمة المرور بنجاح!',
      categoryAdded: 'تم إضافة التصنيف بنجاح!',
      categoryError: 'حدث خطأ أو التصنيف موجود',
      comicAdded: 'تم إضافة الكوميكس بنجاح!',
      comicError: 'حدث خطأ أثناء الحفظ',
      chapterAdded: 'تم إضافة الفصل بنجاح!',
      chapterError: 'حدث خطأ أثناء الحفظ',
      uploadingImages: 'جاري رفع الصور، يرجى الانتظار...',
      deletedSuccessfully: 'تم الحذف بنجاح',
      exportComplete: 'تم التصدير بنجاح!',
      importComplete: 'تم الاستيراد بنجاح!',
      dataFileError: 'خطأ في ملف البيانات',
      deleteAllConfirm: 'هل أنت متأكد من حذف جميع البيانات؟',
      deleteFinalConfirm: 'تأكيد أخير: سيتم حذف كل شيء نهائياً!',
      fillAllFields: 'يرجى ملء جميع الحقول',
      selectAtLeastOne: 'يرجى اختيار صورة واحدة على الأقل',
      
      // Footer
      footerDesc: 'أكبر مكتبة كوميكس عربية مجانية',
      navigation: 'التنقل',
      genres: 'التصنيفات',
      admin: 'الإدارة',
      allRights: 'جميع الحقوق محفوظة',
      
      // Empty States
      noComics: 'لا يوجد كوميكس',
      noUpdates: 'لا توجد تحديثات',
      noResultsFound: 'لم يتم العثور على نتائج',
      
      // Languages
      language: 'اللغة',
      arabic: 'العربية',
      english: 'English',
      turkish: 'Türkçe',
      french: 'Français',
      spanish: 'Español',
      portuguese: 'Português',
      german: 'Deutsch',
      japanese: '日本語',
      korean: '한국어',
      chinese: '中文'
    },
    
    en: {
      // Navigation
      home: 'Home',
      browse: 'Browse',
      trending: 'Trending',
      latest: 'Latest',
      search: 'Search...',
      searchCtrlK: 'Search... (Ctrl+K)',
      signUp: 'Sign Up',
      login: 'Login',
      logout: 'Logout',
      dashboard: 'Dashboard',
      site: 'Site',
      
      // Hero
      heroBadge: '📚 Largest Arabic Manga Library',
      heroTitle1: 'Discover a World of',
      heroTitle2: 'Comics & Manga',
      heroDesc: 'Thousands of comics in high quality, free and ad-free.',
      startReading: 'Start Reading',
      
      // Sections
      trendingComics: 'Trending Comics',
      trendingNovels: 'Trending Novels',
      latestUpdates: 'Latest Updates',
      browseAll: 'Browse All',
      viewAll: 'View All',
      
      // Comic Card
      readNow: 'Read Now',
      views: 'Views',
      chapters: 'Chapters',
      pages: 'Pages',
      rating: 'Rating',
      
      // Categories
      allCategories: 'All',
      
      // Comic Detail
      synopsis: 'Synopsis',
      by: 'by',
      startReadingBtn: 'Start Reading',
      chaptersList: 'Chapters',
      noChapters: 'No Chapters Yet',
      noDescription: 'No description available',
      
      // Reader
      prevChapter: 'Previous',
      nextChapter: 'Next',
      page: 'Page',
      of: 'of',
      toggleMode: 'Toggle Mode',
      zoomIn: 'Zoom In',
      zoomOut: 'Zoom Out',
      close: 'Close',
      noPages: 'No Pages',
      loading: 'Loading...',
      
      // Browse
      browseAllComics: 'Browse All Comics',
      sortBy: 'Sort by:',
      latestFirst: 'Latest First',
      mostPopular: 'Most Popular',
      highestRating: 'Highest Rating',
      az: 'A - Z',
      gridView: 'Grid',
      listView: 'List',
      showing: 'Showing',
      results: 'results',
      noResults: 'No results found',
      trySearch: 'Try searching with different keywords',
      resetFilters: 'Reset Filters',
      
      // Admin Dashboard
      quickActions: 'Quick Actions',
      addNewComic: 'Add New Comic',
      uploadChapters: 'Upload Chapters',
      manageCategories: 'Manage Categories',
      systemInfo: 'System Info',
      platform: 'Platform',
      version: 'Version',
      backend: 'Backend',
      hosting: 'Hosting',
      
      // Admin Comics
      manageComics: 'Manage Comics',
      addComic: 'Add Comic',
      title: 'Title',
      category: 'Category',
      author: 'Author',
      description: 'Description',
      coverImage: 'Cover Image',
      clickOrDrag: 'Click or drag to upload cover',
      saveComic: 'Save Comic',
      cancel: 'Cancel',
      selectCategory: 'Select Category',
      noComicsYet: 'No Comics Yet',
      startByAdding: 'Start by adding your first comic',
      deleteComic: 'Delete',
      
      // Admin Chapters
      manageChapters: 'Manage Chapters',
      addChapter: 'Add Chapter',
      comic: 'Comic',
      chapterNumber: 'Chapter Number',
      chapterTitle: 'Chapter Title',
      pagesImages: 'Page Images',
      clickOrDragImages: 'Click or drag images here',
      multipleFiles: 'You can select multiple files',
      saveChapter: 'Save Chapter',
      selectComic: 'Select Comic',
      noChaptersYet: 'No Chapters Yet',
      startByAddingChapter: 'Start by adding your first chapter',
      
      // Admin Categories
      manageCategoriesTitle: 'Manage Categories',
      addCategory: 'Add Category',
      categoryName: 'Category Name',
      add: 'Add',
      noCategoriesYet: 'No Categories Yet',
      startByAddingCategory: 'Start by adding your first category',
      
      // Admin Settings
      settings: 'Settings',
      changePassword: 'Change Password',
      currentPassword: 'Current Password',
      newPassword: 'New Password',
      confirmPassword: 'Confirm Password',
      saveChanges: 'Save Changes',
      exportData: 'Export Data',
      exportDesc: 'Export all site data as a JSON backup file',
      exportJson: 'Export JSON',
      importData: 'Import Data',
      importDesc: 'Import data from a previously exported JSON file',
      dropJsonHere: 'Drop JSON file here',
      dangerZone: 'Danger Zone',
      dangerDesc: 'Permanently delete all data. This cannot be undone.',
      deleteAllData: 'Delete All Data',
      
      // Messages
      passwordMismatch: 'Passwords do not match',
      currentPasswordIncorrect: 'Current password is incorrect',
      passwordChanged: 'Password changed successfully!',
      categoryAdded: 'Category added successfully!',
      categoryError: 'Error or category already exists',
      comicAdded: 'Comic added successfully!',
      comicError: 'Error saving comic',
      chapterAdded: 'Chapter added successfully!',
      chapterError: 'Error saving chapter',
      uploadingImages: 'Uploading images, please wait...',
      deletedSuccessfully: 'Deleted successfully',
      exportComplete: 'Export completed!',
      importComplete: 'Import completed successfully!',
      dataFileError: 'Error in data file',
      deleteAllConfirm: 'Are you sure you want to delete ALL data?',
      deleteFinalConfirm: 'FINAL WARNING: This will permanently delete everything!',
      fillAllFields: 'Please fill all fields',
      selectAtLeastOne: 'Please select at least one image',
      
      // Footer
      footerDesc: 'The largest free Arabic manga library',
      navigation: 'Navigation',
      genres: 'Genres',
      admin: 'Admin',
      allRights: 'All rights reserved',
      
      // Empty States
      noComics: 'No Comics',
      noUpdates: 'No Updates',
      noResultsFound: 'No Results Found',
      
      // Languages
      language: 'Language',
      arabic: 'العربية',
      english: 'English',
      turkish: 'Türkçe',
      french: 'Français',
      spanish: 'Español',
      portuguese: 'Português',
      german: 'Deutsch',
      japanese: '日本語',
      korean: '한국어',
      chinese: '中文'
    },
    
    tr: {
      home: 'Ana Sayfa',
      browse: 'Gözat',
      trending: 'Popüler',
      latest: 'Son Eklenenler',
      search: 'Ara...',
      searchCtrlK: 'Ara... (Ctrl+K)',
      signUp: 'Kayıt Ol',
      login: 'Giriş Yap',
      logout: 'Çıkış',
      dashboard: 'Kontrol Paneli',
      site: 'Site',
      heroBadge: '📚 En Büyük Arapça Manga Kütüphanesi',
      heroTitle1: 'Manga ve',
      heroTitle2: 'Çizgi Roman Dünyasını Keşfet',
      heroDesc: 'Binlerce yüksek kaliteli çizgi roman, ücretsiz ve reklamsız.',
      startReading: 'Okumaya Başla',
      trendingComics: 'Popüler Çizgi Romanlar',
      trendingNovels: 'Popüler Romanlar',
      latestUpdates: 'Son Güncellemeler',
      viewAll: 'Tümünü Gör',
      readNow: 'Hemen Oku',
      views: 'Görüntülenme',
      chapters: 'Bölümler',
      pages: 'Sayfalar',
      rating: 'Puan',
      allCategories: 'Tümü',
      synopsis: 'Özet',
      by: 'yazan',
      startReadingBtn: 'Okumaya Başla',
      chaptersList: 'Bölümler',
      noChapters: 'Henüz Bölüm Yok',
      noDescription: 'Açıklama mevcut değil',
      prevChapter: 'Önceki',
      nextChapter: 'Sonraki',
      page: 'Sayfa',
      of: '/',
      toggleMode: 'Mod Değiştir',
      zoomIn: 'Yakınlaştır',
      zoomOut: 'Uzaklaştır',
      close: 'Kapat',
      noPages: 'Sayfa Yok',
      loading: 'Yükleniyor...',
      browseAllComics: 'Tüm Çizgi Romanlara Gözat',
      sortBy: 'Sırala:',
      latestFirst: 'En Yeni',
      mostPopular: 'En Popüler',
      highestRating: 'En Yüksek Puan',
      az: 'A - Z',
      results: 'sonuç',
      noResults: 'Sonuç bulunamadı',
      trySearch: 'Farklı anahtar kelimelerle aramayı deneyin',
      quickActions: 'Hızlı İşlemler',
      addNewComic: 'Yeni Çizgi Roman Ekle',
      manageComics: 'Çizgi Romanları Yönet',
      addComic: 'Çizgi Roman Ekle',
      title: 'Başlık',
      category: 'Kategori',
      author: 'Yazar',
      description: 'Açıklama',
      coverImage: 'Kapak Resmi',
      saveComic: 'Kaydet',
      cancel: 'İptal',
      selectCategory: 'Kategori Seç',
      noComicsYet: 'Henüz Çizgi Roman Yok',
      startByAdding: 'İlk çizgi romanınızı ekleyerek başlayın',
      manageChapters: 'Bölümleri Yönet',
      addChapter: 'Bölüm Ekle',
      chapterNumber: 'Bölüm Numarası',
      chapterTitle: 'Bölüm Başlığı',
      pagesImages: 'Sayfa Resimleri',
      saveChapter: 'Kaydet',
      selectComic: 'Çizgi Roman Seç',
      noChaptersYet: 'Henüz Bölüm Yok',
      manageCategoriesTitle: 'Kategorileri Yönet',
      addCategory: 'Kategori Ekle',
      categoryName: 'Kategori Adı',
      add: 'Ekle',
      noCategoriesYet: 'Henüz Kategori Yok',
      settings: 'Ayarlar',
      changePassword: 'Şifre Değiştir',
      currentPassword: 'Mevcut Şifre',
      newPassword: 'Yeni Şifre',
      confirmPassword: 'Şifre Tekrar',
      saveChanges: 'Değişiklikleri Kaydet',
      exportData: 'Verileri Dışa Aktar',
      exportJson: 'JSON Dışa Aktar',
      importData: 'Verileri İçe Aktar',
      dangerZone: 'Tehlike Bölgesi',
      dangerDesc: 'Tüm verileri kalıcı olarak silin. Geri alınamaz.',
      deleteAllData: 'Tüm Verileri Sil',
      footerDesc: 'En büyük ücretsiz Arapça manga kütüphanesi',
      navigation: 'Gezinme',
      genres: 'Türler',
      admin: 'Yönetim',
      allRights: 'Tüm hakları saklıdır',
      language: 'Dil',
      arabic: 'العربية',
      english: 'English',
      turkish: 'Türkçe',
      passwordMismatch: 'Şifreler eşleşmiyor',
      currentPasswordIncorrect: 'Mevcut şifre yanlış',
      passwordChanged: 'Şifre başarıyla değiştirildi!',
      categoryAdded: 'Kategori başarıyla eklendi!',
      comicAdded: 'Çizgi roman başarıyla eklendi!',
      chapterAdded: 'Bölüm başarıyla eklendi!',
      deletedSuccessfully: 'Başarıyla silindi',
      uploadChapters: 'Bölüm Yükle',
      manageCategories: 'Kategorileri Yönet',
      systemInfo: 'Sistem Bilgisi',
      platform: 'Platform',
      version: 'Sürüm',
      backend: 'Arka Plan',
      hosting: 'Barındırma',
      clickOrDrag: 'Kapak yüklemek için tıklayın veya sürükleyin',
      clickOrDragImages: 'Resimleri buraya tıklayın veya sürükleyin',
      multipleFiles: 'Birden fazla dosya seçebilirsiniz',
      uploadingImages: 'Resimler yükleniyor, lütfen bekleyin...',
      exportComplete: 'Dışa aktarma tamamlandı!',
      importComplete: 'İçe aktarma başarıyla tamamlandı!',
      fillAllFields: 'Lütfen tüm alanları doldurun',
      selectAtLeastOne: 'Lütfen en az bir resim seçin',
      gridView: 'Izgara',
      listView: 'Liste',
      showing: 'Gösteriliyor',
      site: 'Site',
      exportDesc: 'Tüm site verilerini JSON yedek dosyası olarak dışa aktarın',
      importDesc: 'Daha önce dışa aktarılmış bir JSON dosyasından veri içe aktarın',
      dropJsonHere: 'JSON dosyasını buraya bırakın',
      noDescription: 'Açıklama mevcut değil',
      deleteComic: 'Sil'
    },
    
    fr: {
      home: 'Accueil',
      browse: 'Parcourir',
      trending: 'Tendances',
      latest: 'Dernières',
      search: 'Rechercher...',
      searchCtrlK: 'Rechercher... (Ctrl+K)',
      signUp: "S'inscrire",
      login: 'Connexion',
      logout: 'Déconnexion',
      dashboard: 'Tableau de bord',
      site: 'Site',
      heroBadge: '📚 Plus grande bibliothèque de manga arabe',
      heroTitle1: 'Découvrez un monde de',
      heroTitle2: 'Bandes dessinées',
      heroDesc: 'Des milliers de bandes dessinées en haute qualité, gratuites et sans publicité.',
      startReading: 'Commencer à lire',
      trendingComics: 'Bandes dessinées tendance',
      trendingNovels: 'Romans tendance',
      latestUpdates: 'Dernières mises à jour',
      viewAll: 'Voir tout',
      readNow: 'Lire maintenant',
      views: 'Vues',
      chapters: 'Chapitres',
      pages: 'Pages',
      rating: 'Note',
      allCategories: 'Toutes',
      synopsis: 'Synopsis',
      by: 'par',
      startReadingBtn: 'Commencer à lire',
      chaptersList: 'Chapitres',
      noChapters: 'Pas encore de chapitres',
      noDescription: 'Aucune description disponible',
      prevChapter: 'Précédent',
      nextChapter: 'Suivant',
      page: 'Page',
      of: 'sur',
      toggleMode: 'Changer le mode',
      zoomIn: 'Zoom avant',
      zoomOut: 'Zoom arrière',
      close: 'Fermer',
      noPages: 'Pas de pages',
      loading: 'Chargement...',
      browseAllComics: 'Parcourir toutes les bandes dessinées',
      sortBy: 'Trier par:',
      latestFirst: 'Plus récent',
      mostPopular: 'Plus populaire',
      highestRating: 'Mieux noté',
      az: 'A - Z',
      results: 'résultats',
      noResults: 'Aucun résultat trouvé',
      trySearch: 'Essayez avec d\'autres mots-clés',
      quickActions: 'Actions rapides',
      addNewComic: 'Ajouter une bande dessinée',
      manageComics: 'Gérer les bandes dessinées',
      addComic: 'Ajouter',
      title: 'Titre',
      category: 'Catégorie',
      author: 'Auteur',
      description: 'Description',
      coverImage: 'Image de couverture',
      saveComic: 'Enregistrer',
      cancel: 'Annuler',
      selectCategory: 'Sélectionner une catégorie',
      noComicsYet: 'Pas encore de bandes dessinées',
      startByAdding: 'Commencez par ajouter votre première bande dessinée',
      manageChapters: 'Gérer les chapitres',
      addChapter: 'Ajouter un chapitre',
      chapterNumber: 'Numéro du chapitre',
      chapterTitle: 'Titre du chapitre',
      pagesImages: 'Images des pages',
      saveChapter: 'Enregistrer',
      selectComic: 'Sélectionner une bande dessinée',
      noChaptersYet: 'Pas encore de chapitres',
      manageCategoriesTitle: 'Gérer les catégories',
      addCategory: 'Ajouter une catégorie',
      categoryName: 'Nom de la catégorie',
      add: 'Ajouter',
      noCategoriesYet: 'Pas encore de catégories',
      settings: 'Paramètres',
      changePassword: 'Changer le mot de passe',
      currentPassword: 'Mot de passe actuel',
      newPassword: 'Nouveau mot de passe',
      confirmPassword: 'Confirmer le mot de passe',
      saveChanges: 'Enregistrer les modifications',
      exportData: 'Exporter les données',
      exportJson: 'Exporter JSON',
      importData: 'Importer les données',
      dangerZone: 'Zone de danger',
      dangerDesc: 'Supprimer définitivement toutes les données. Irréversible.',
      deleteAllData: 'Supprimer toutes les données',
      footerDesc: 'La plus grande bibliothèque de manga arabe gratuite',
      navigation: 'Navigation',
      genres: 'Genres',
      admin: 'Admin',
      allRights: 'Tous droits réservés',
      language: 'Langue',
      arabic: 'العربية',
      english: 'English',
      french: 'Français',
      passwordMismatch: 'Les mots de passe ne correspondent pas',
      currentPasswordIncorrect: 'Le mot de passe actuel est incorrect',
      passwordChanged: 'Mot de passe modifié avec succès!',
      categoryAdded: 'Catégorie ajoutée avec succès!',
      comicAdded: 'Bande dessinée ajoutée avec succès!',
      chapterAdded: 'Chapitre ajouté avec succès!',
      deletedSuccessfully: 'Supprimé avec succès',
      uploadChapters: 'Télécharger des chapitres',
      manageCategories: 'Gérer les catégories',
      systemInfo: 'Info système',
      platform: 'Plateforme',
      version: 'Version',
      backend: 'Backend',
      hosting: 'Hébergement',
      clickOrDrag: 'Cliquez ou glissez pour télécharger la couverture',
      clickOrDragImages: 'Cliquez ou glissez les images ici',
      multipleFiles: 'Vous pouvez sélectionner plusieurs fichiers',
      uploadingImages: 'Téléchargement des images, veuillez patienter...',
      exportComplete: 'Exportation terminée!',
      importComplete: 'Importation réussie!',
      fillAllFields: 'Veuillez remplir tous les champs',
      selectAtLeastOne: 'Veuillez sélectionner au moins une image',
      gridView: 'Grille',
      listView: 'Liste',
      showing: 'Affichage',
      exportDesc: 'Télécharger toutes les données du site en JSON',
      importDesc: 'Importer les données depuis un fichier JSON',
      dropJsonHere: 'Déposez le fichier JSON ici',
      deleteComic: 'Supprimer'
    },
    
    es: {
      home: 'Inicio',
      browse: 'Explorar',
      trending: 'Tendencias',
      latest: 'Últimos',
      search: 'Buscar...',
      searchCtrlK: 'Buscar... (Ctrl+K)',
      signUp: 'Registrarse',
      login: 'Iniciar sesión',
      logout: 'Cerrar sesión',
      dashboard: 'Panel de control',
      site: 'Sitio',
      heroBadge: '📚 Mayor biblioteca de manga árabe',
      heroTitle1: 'Descubre un mundo de',
      heroTitle2: 'Cómics y manga',
      heroDesc: 'Miles de cómics en alta calidad, gratis y sin anuncios.',
      startReading: 'Empezar a leer',
      trendingComics: 'Cómics populares',
      trendingNovels: 'Novelas populares',
      latestUpdates: 'Últimas actualizaciones',
      viewAll: 'Ver todo',
      readNow: 'Leer ahora',
      views: 'Visitas',
      chapters: 'Capítulos',
      pages: 'Páginas',
      rating: 'Puntuación',
      allCategories: 'Todos',
      synopsis: 'Sinopsis',
      by: 'por',
      startReadingBtn: 'Empezar a leer',
      chaptersList: 'Capítulos',
      noChapters: 'Sin capítulos aún',
      noDescription: 'Sin descripción',
      prevChapter: 'Anterior',
      nextChapter: 'Siguiente',
      page: 'Página',
      of: 'de',
      toggleMode: 'Cambiar modo',
      zoomIn: 'Acercar',
      zoomOut: 'Alejar',
      close: 'Cerrar',
      noPages: 'Sin páginas',
      loading: 'Cargando...',
      browseAllComics: 'Explorar todos los cómics',
      sortBy: 'Ordenar por:',
      latestFirst: 'Más reciente',
      mostPopular: 'Más popular',
      highestRating: 'Mejor valorado',
      az: 'A - Z',
      results: 'resultados',
      noResults: 'No se encontraron resultados',
      trySearch: 'Intenta buscar con otras palabras',
      quickActions: 'Acciones rápidas',
      addNewComic: 'Agregar cómic',
      manageComics: 'Gestionar cómics',
      addComic: 'Agregar',
      title: 'Título',
      category: 'Categoría',
      author: 'Autor',
      description: 'Descripción',
      coverImage: 'Imagen de portada',
      saveComic: 'Guardar',
      cancel: 'Cancelar',
      selectCategory: 'Seleccionar categoría',
      noComicsYet: 'Sin cómics aún',
      startByAdding: 'Comienza agregando tu primer cómic',
      manageChapters: 'Gestionar capítulos',
      addChapter: 'Agregar capítulo',
      chapterNumber: 'Número de capítulo',
      chapterTitle: 'Título del capítulo',
      pagesImages: 'Imágenes de páginas',
      saveChapter: 'Guardar',
      selectComic: 'Seleccionar cómic',
      noChaptersYet: 'Sin capítulos aún',
      manageCategoriesTitle: 'Gestionar categorías',
      addCategory: 'Agregar categoría',
      categoryName: 'Nombre de categoría',
      add: 'Agregar',
      noCategoriesYet: 'Sin categorías aún',
      settings: 'Configuración',
      changePassword: 'Cambiar contraseña',
      currentPassword: 'Contraseña actual',
      newPassword: 'Nueva contraseña',
      confirmPassword: 'Confirmar contraseña',
      saveChanges: 'Guardar cambios',
      exportData: 'Exportar datos',
      exportJson: 'Exportar JSON',
      importData: 'Importar datos',
      dangerZone: 'Zona de peligro',
      dangerDesc: 'Eliminar permanentemente todos los datos. No se puede deshacer.',
      deleteAllData: 'Eliminar todos los datos',
      footerDesc: 'La mayor biblioteca de manga árabe gratuita',
      navigation: 'Navegación',
      genres: 'Géneros',
      admin: 'Admin',
      allRights: 'Todos los derechos reservados',
      language: 'Idioma',
      arabic: 'العربية',
      english: 'English',
      spanish: 'Español',
      passwordMismatch: 'Las contraseñas no coinciden',
      currentPasswordIncorrect: 'La contraseña actual es incorrecta',
      passwordChanged: '¡Contraseña cambiada con éxito!',
      categoryAdded: '¡Categoría agregada con éxito!',
      comicAdded: '¡Cómic agregado con éxito!',
      chapterAdded: '¡Capítulo agregado con éxito!',
      deletedSuccessfully: 'Eliminado con éxito',
      uploadChapters: 'Subir capítulos',
      manageCategories: 'Gestionar categorías',
      systemInfo: 'Info del sistema',
      platform: 'Plataforma',
      version: 'Versión',
      backend: 'Backend',
      hosting: 'Hosting',
      clickOrDrag: 'Clic o arrastra para subir portada',
      clickOrDragImages: 'Clic o arrastra imágenes aquí',
      multipleFiles: 'Puedes seleccionar varios archivos',
      uploadingImages: 'Subiendo imágenes, por favor espera...',
      exportComplete: '¡Exportación completada!',
      importComplete: '¡Importación completada!',
      fillAllFields: 'Por favor completa todos los campos',
      selectAtLeastOne: 'Por favor selecciona al menos una imagen',
      gridView: 'Cuadrícula',
      listView: 'Lista',
      showing: 'Mostrando',
      exportDesc: 'Descargar todos los datos del sitio en JSON',
      importDesc: 'Importar datos desde un archivo JSON',
      dropJsonHere: 'Suelta el archivo JSON aquí',
      deleteComic: 'Eliminar'
    },
    
    pt: {
      home: 'Início',
      browse: 'Explorar',
      trending: 'Tendências',
      latest: 'Últimos',
      search: 'Pesquisar...',
      searchCtrlK: 'Pesquisar... (Ctrl+K)',
      signUp: 'Cadastrar',
      login: 'Entrar',
      logout: 'Sair',
      dashboard: 'Painel',
      site: 'Site',
      heroBadge: '📚 Maior biblioteca de manga árabe',
      heroTitle1: 'Descubra um mundo de',
      heroTitle2: 'Quadrinhos e mangá',
      heroDesc: 'Milhares de quadrinhos em alta qualidade, grátis e sem anúncios.',
      startReading: 'Começar a ler',
      trendingComics: 'Quadrinhos populares',
      trendingNovels: 'Romances populares',
      latestUpdates: 'Últimas atualizações',
      viewAll: 'Ver tudo',
      readNow: 'Ler agora',
      views: 'Visualizações',
      chapters: 'Capítulos',
      pages: 'Páginas',
      rating: 'Avaliação',
      allCategories: 'Todos',
      synopsis: 'Sinopse',
      by: 'por',
      startReadingBtn: 'Começar a ler',
      chaptersList: 'Capítulos',
      noChapters: 'Sem capítulos ainda',
      noDescription: 'Sem descrição',
      prevChapter: 'Anterior',
      nextChapter: 'Próximo',
      page: 'Página',
      of: 'de',
      toggleMode: 'Alternar modo',
      zoomIn: 'Ampliar',
      zoomOut: 'Reduzir',
      close: 'Fechar',
      noPages: 'Sem páginas',
      loading: 'Carregando...',
      browseAllComics: 'Explorar todos os quadrinhos',
      sortBy: 'Ordenar por:',
      latestFirst: 'Mais recente',
      mostPopular: 'Mais popular',
      highestRating: 'Melhor avaliado',
      az: 'A - Z',
      results: 'resultados',
      noResults: 'Nenhum resultado encontrado',
      trySearch: 'Tente pesquisar com outras palavras',
      quickActions: 'Ações rápidas',
      addNewComic: 'Adicionar quadrinho',
      manageComics: 'Gerenciar quadrinhos',
      addComic: 'Adicionar',
      title: 'Título',
      category: 'Categoria',
      author: 'Autor',
      description: 'Descrição',
      coverImage: 'Imagem de capa',
      saveComic: 'Salvar',
      cancel: 'Cancelar',
      selectCategory: 'Selecionar categoria',
      noComicsYet: 'Sem quadrinhos ainda',
      startByAdding: 'Comece adicionando seu primeiro quadrinho',
      manageChapters: 'Gerenciar capítulos',
      addChapter: 'Adicionar capítulo',
      chapterNumber: 'Número do capítulo',
      chapterTitle: 'Título do capítulo',
      pagesImages: 'Imagens das páginas',
      saveChapter: 'Salvar',
      selectComic: 'Selecionar quadrinho',
      noChaptersYet: 'Sem capítulos ainda',
      manageCategoriesTitle: 'Gerenciar categorias',
      addCategory: 'Adicionar categoria',
      categoryName: 'Nome da categoria',
      add: 'Adicionar',
      noCategoriesYet: 'Sem categorias ainda',
      settings: 'Configurações',
      changePassword: 'Alterar senha',
      currentPassword: 'Senha atual',
      newPassword: 'Nova senha',
      confirmPassword: 'Confirmar senha',
      saveChanges: 'Salvar alterações',
      exportData: 'Exportar dados',
      exportJson: 'Exportar JSON',
      importData: 'Importar dados',
      dangerZone: 'Zona de perigo',
      dangerDesc: 'Excluir permanentemente todos os dados. Irreversível.',
      deleteAllData: 'Excluir todos os dados',
      footerDesc: 'A maior biblioteca de mangá árabe gratuita',
      navigation: 'Navegação',
      genres: 'Gêneros',
      admin: 'Admin',
      allRights: 'Todos os direitos reservados',
      language: 'Idioma',
      arabic: 'العربية',
      english: 'English',
      portuguese: 'Português',
      passwordMismatch: 'As senhas não coincidem',
      currentPasswordIncorrect: 'A senha atual está incorreta',
      passwordChanged: 'Senha alterada com sucesso!',
      categoryAdded: 'Categoria adicionada com sucesso!',
      comicAdded: 'Quadrinho adicionado com sucesso!',
      chapterAdded: 'Capítulo adicionado com sucesso!',
      deletedSuccessfully: 'Excluído com sucesso',
      uploadChapters: 'Carregar capítulos',
      manageCategories: 'Gerenciar categorias',
      systemInfo: 'Info do sistema',
      platform: 'Plataforma',
      version: 'Versão',
      backend: 'Backend',
      hosting: 'Hospedagem',
      clickOrDrag: 'Clique ou arraste para carregar a capa',
      clickOrDragImages: 'Clique ou arraste imagens aqui',
      multipleFiles: 'Você pode selecionar vários arquivos',
      uploadingImages: 'Carregando imagens, por favor aguarde...',
      exportComplete: 'Exportação concluída!',
      importComplete: 'Importação concluída com sucesso!',
      fillAllFields: 'Por favor preencha todos os campos',
      selectAtLeastOne: 'Por favor selecione pelo menos uma imagem',
      gridView: 'Grade',
      listView: 'Lista',
      showing: 'Mostrando',
      exportDesc: 'Baixar todos os dados do site em JSON',
      importDesc: 'Importar dados de um arquivo JSON',
      dropJsonHere: 'Solte o arquivo JSON aqui',
      deleteComic: 'Excluir'
    }
  },

  // Initialize i18n
  init() {
    // Check URL for language parameter
    const urlParams = new URLSearchParams(window.location.search);
    const langParam = urlParams.get('lang');
    
    if (langParam && this.supported.includes(langParam)) {
      this.current = langParam;
      localStorage.setItem('sedbox_lang', langParam);
    } else {
      // Check saved preference
      const saved = localStorage.getItem('sedbox_lang');
      if (saved && this.supported.includes(saved)) {
        this.current = saved;
      } else {
        // Detect from browser/device
        const browserLang = navigator.language || navigator.userLanguage;
        this.current = this.detectLanguage(browserLang);
      }
    }
    
    this.applyLanguage();
    return this.current;
  },

  // Detect language from browser
  detectLanguage(browserLang) {
    if (!browserLang) return 'en';
    
    const lang = browserLang.toLowerCase().split('-')[0];
    
    if (this.supported.includes(lang)) {
      return lang;
    }
    
    // Fallback mappings
    const mappings = {
      'ar': 'ar',
      'he': 'ar',
      'fa': 'ar',
      'ur': 'ar',
      'tr': 'tr',
      'fr': 'fr',
      'es': 'es',
      'pt': 'pt',
      'de': 'de',
      'ja': 'ja',
      'ko': 'ko',
      'zh': 'zh'
    };
    
    return mappings[lang] || 'en';
  },

  // Get translation
  t(key) {
    const lang = this.translations[this.current];
    if (lang && lang[key]) {
      return lang[key];
    }
    // Fallback to English
    if (this.translations.en && this.translations.en[key]) {
      return this.translations.en[key];
    }
    return key;
  },

  // Apply language to document
  applyLanguage() {
    const isRtl = this.rtlLanguages.includes(this.current);
    
    // Set HTML direction and lang
    document.documentElement.dir = isRtl ? 'rtl' : 'ltr';
    document.documentElement.lang = this.current;
    
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      const translation = this.t(key);
      if (translation) {
        el.textContent = translation;
      }
    });
    
    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      const translation = this.t(key);
      if (translation) {
        el.placeholder = translation;
      }
    });
  },

  // Change language
  changeLanguage(lang) {
    if (!this.supported.includes(lang)) return;
    
    this.current = lang;
    localStorage.setItem('sedbox_lang', lang);
    
    // Update URL without reload
    const url = new URL(window.location);
    url.searchParams.set('lang', lang);
    window.history.replaceState({}, '', url);
    
    this.applyLanguage();
    
    // Trigger event for custom handlers
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
  },

  // Get current language direction
  getDirection() {
    return this.rtlLanguages.includes(this.current) ? 'rtl' : 'ltr';
  },

  // Get language name in its own language
  getLanguageName(code) {
    const names = {
      ar: 'العربية',
      en: 'English',
      tr: 'Türkçe',
      fr: 'Français',
      es: 'Español',
      pt: 'Português',
      de: 'Deutsch',
      ja: '日本語',
      ko: '한국어',
      zh: '中文'
    };
    return names[code] || code;
  },

  // Get flag emoji
  getFlag(code) {
    const flags = {
      ar: '🇸🇦',
      en: '🇺🇸',
      tr: '🇹🇷',
      fr: '🇫🇷',
      es: '🇪🇸',
      pt: '🇵🇹',
      de: '🇩🇪',
      ja: '🇯🇵',
      ko: '🇰🇷',
      zh: '🇨🇳'
    };
    return flags[code] || '🌐';
  }
};

// Auto-initialize
document.addEventListener('DOMContentLoaded', function() {
  I18N.init();
});

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = I18N;
}
