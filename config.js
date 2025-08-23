// Configuration file for Proxy Bot App
// تكوين تطبيق بوت البروكسي

export const CONFIG = {
  // Server Configuration - تكوين الخادم
  // IMPORTANT: Change this URL to your actual server URL
  // مهم: غيّر هذا الرابط إلى رابط خادمك الفعلي
  
  // For local testing (للتجربة المحلية):
  // API_BASE_URL: 'http://localhost:5000/api',
  
  // For cloud deployment (للنشر السحابي):
  // Replace with your actual server URL
  API_BASE_URL: 'https://your-server-url.herokuapp.com/api',
  
  // Alternative examples (أمثلة بديلة):
  // API_BASE_URL: 'https://your-app.railway.app/api',
  // API_BASE_URL: 'https://your-app.render.com/api',
  // API_BASE_URL: 'https://your-domain.com/api',
  
  // Bot Configuration - تكوين البوت
  BOT_NAME: 'Proxy Bot',
  BOT_VERSION: '1.0.0',
  
  // App Settings - إعدادات التطبيق
  REFRESH_INTERVAL: 5000, // 5 seconds
  MAX_RETRIES: 3,
  TIMEOUT: 10000, // 10 seconds
  
  // UI Configuration - تكوين واجهة المستخدم
  THEME: {
    PRIMARY_COLOR: '#2196F3',
    SECONDARY_COLOR: '#03DAC6',
    BACKGROUND_COLOR: '#FFFFFF',
    SURFACE_COLOR: '#F5F5F5',
  },
  
  // Features Toggle - تبديل الميزات
  FEATURES: {
    AUTO_REFRESH: true,
    PUSH_NOTIFICATIONS: true,
    DARK_MODE: false,
  }
};

// Instructions for setup:
// تعليمات الإعداد:
// 
// 1. Deploy your Python bot to a cloud service
//    انشر بوت Python على خدمة سحابية
// 
// 2. Update API_BASE_URL with your server URL
//    حدث API_BASE_URL برابط خادمك
// 
// 3. Build and install the APK
//    ابني وثبت ملف APK
// 
// 4. The app will connect to your cloud server
//    التطبيق سيتصل بخادمك السحابي

export default CONFIG;