import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Provider as PaperProvider, MD3LightTheme } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import Icon from 'react-native-vector-icons/MaterialIcons';

// استيراد الصفحات
import BotManagementScreen from './screens/BotManagementScreen';
import ProxyManagementScreen from './screens/ProxyManagementScreen';
import UserManagementScreen from './screens/UserManagementScreen';
import OrderManagementScreen from './screens/OrderManagementScreen';
import PaymentManagementScreen from './screens/PaymentManagementScreen';
import SettingsScreen from './screens/SettingsScreen';

const Tab = createBottomTabNavigator();

// تخصيص الألوان
const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#2196F3',
    primaryContainer: '#E3F2FD',
    secondary: '#03DAC6',
    background: '#FFFFFF',
    surface: '#F5F5F5',
  },
};

export default function App() {
  return (
    <PaperProvider theme={theme}>
      <NavigationContainer>
        <StatusBar style="auto" />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            tabBarIcon: ({ focused, color, size }) => {
              let iconName;

              switch (route.name) {
                case 'BotManagement':
                  iconName = 'settings';
                  break;
                case 'ProxyManagement':
                  iconName = 'dns';
                  break;
                case 'UserManagement':
                  iconName = 'people';
                  break;
                case 'OrderManagement':
                  iconName = 'shopping-cart';
                  break;
                case 'PaymentManagement':
                  iconName = 'payment';
                  break;
                case 'Settings':
                  iconName = 'settings-applications';
                  break;
                default:
                  iconName = 'help';
              }

              return <Icon name={iconName} size={size} color={color} />;
            },
            tabBarActiveTintColor: theme.colors.primary,
            tabBarInactiveTintColor: 'gray',
            tabBarStyle: {
              backgroundColor: theme.colors.surface,
              borderTopWidth: 1,
              borderTopColor: '#E0E0E0',
            },
            headerStyle: {
              backgroundColor: theme.colors.primary,
            },
            headerTintColor: '#FFFFFF',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          })}
        >
          <Tab.Screen 
            name="BotManagement" 
            component={BotManagementScreen}
            options={{
              title: 'إدارة البوت',
              tabBarLabel: 'البوت'
            }}
          />
          <Tab.Screen 
            name="ProxyManagement" 
            component={ProxyManagementScreen}
            options={{
              title: 'إدارة البروكسيات',
              tabBarLabel: 'البروكسيات'
            }}
          />
          <Tab.Screen 
            name="UserManagement" 
            component={UserManagementScreen}
            options={{
              title: 'إدارة المستخدمين',
              tabBarLabel: 'المستخدمين'
            }}
          />
          <Tab.Screen 
            name="OrderManagement" 
            component={OrderManagementScreen}
            options={{
              title: 'إدارة الطلبات',
              tabBarLabel: 'الطلبات'
            }}
          />
          <Tab.Screen 
            name="PaymentManagement" 
            component={PaymentManagementScreen}
            options={{
              title: 'إدارة المدفوعات',
              tabBarLabel: 'المدفوعات'
            }}
          />
          <Tab.Screen 
            name="Settings" 
            component={SettingsScreen}
            options={{
              title: 'الإعدادات',
              tabBarLabel: 'الإعدادات'
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
}