import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  TextInput,
  Switch,
  Divider,
  Chip,
  Surface,
  IconButton,
  RadioButton,
  HelperText,
} from 'react-native-paper';
import CloudServerService from '../services/CloudServerService';

export default function SettingsScreen() {
  const [deploymentMode, setDeploymentMode] = useState('termux'); // 'termux' or 'cloud'
  const [sshConfig, setSshConfig] = useState({
    host: '',
    port: '22',
    username: '',
    password: '',
    privateKey: '',
    usePrivateKey: false,
  });
  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const savedConfig = await CloudServerService.loadServerConfig();
      if (savedConfig) {
        setSshConfig(savedConfig);
        setDeploymentMode('cloud');
      }
    } catch (error) {
      console.error('خطأ في تحميل الإعدادات:', error);
    }
  };

  const handleSaveConfig = async () => {
    if (deploymentMode === 'cloud') {
      if (!sshConfig.host || !sshConfig.username) {
        Alert.alert('خطأ', 'يجب إدخال عنوان الخادم واسم المستخدم على الأقل');
        return;
      }

      if (!sshConfig.usePrivateKey && !sshConfig.password) {
        Alert.alert('خطأ', 'يجب إدخال كلمة المرور أو المفتاح الخاص');
        return;
      }

      setLoading(true);
      try {
        await CloudServerService.saveServerConfig(sshConfig);
        Alert.alert('نجح', 'تم حفظ إعدادات الخادم بنجاح');
      } catch (error) {
        Alert.alert('خطأ', 'فشل في حفظ الإعدادات');
      }
      setLoading(false);
    }
  };

  const handleTestConnection = async () => {
    if (!sshConfig.host || !sshConfig.username) {
      Alert.alert('خطأ', 'يجب إدخال عنوان الخادم واسم المستخدم للاختبار');
      return;
    }

    setTestingConnection(true);
    setConnectionStatus(null);

    try {
      const isConnected = await CloudServerService.testSSHConnection(sshConfig);
      setConnectionStatus(isConnected);
      
      if (isConnected) {
        Alert.alert(
          'نجح الاتصال! ✅',
          'تم الاتصال بالخادم بنجاح. يمكنك الآن حفظ الإعدادات واستخدام الخادم السحابي.',
          [{ text: 'ممتاز!' }]
        );
      } else {
        Alert.alert(
          'فشل الاتصال ❌',
          'لم يتم الاتصال بالخادم. تحقق من:\n\n• عنوان الخادم والبورت\n• اسم المستخدم\n• كلمة المرور أو المفتاح الخاص\n• الاتصال بالإنترنت',
          [{ text: 'موافق' }]
        );
      }
    } catch (error) {
      setConnectionStatus(false);
      Alert.alert('خطأ', 'حدث خطأ أثناء اختبار الاتصال');
    }

    setTestingConnection(false);
  };

  const handleResetSettings = () => {
    Alert.alert(
      'إعادة تعيين الإعدادات',
      'هل أنت متأكد من حذف جميع إعدادات الخادم؟',
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'حذف',
          style: 'destructive',
          onPress: () => {
            setSshConfig({
              host: '',
              port: '22',
              username: '',
              password: '',
              privateKey: '',
              usePrivateKey: false,
            });
            setDeploymentMode('termux');
            setConnectionStatus(null);
            Alert.alert('تم', 'تم حذف إعدادات الخادم');
          }
        }
      ]
    );
  };

  return (
    <ScrollView style={styles.container}>
      {/* وضع النشر */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>🚀 وضع تشغيل البوت</Title>
          <Paragraph style={styles.description}>
            اختر طريقة تشغيل البوت
          </Paragraph>

          <View style={styles.radioContainer}>
            <View style={styles.radioOption}>
              <RadioButton
                value="termux"
                status={deploymentMode === 'termux' ? 'checked' : 'unchecked'}
                onPress={() => setDeploymentMode('termux')}
              />
              <View style={styles.radioLabel}>
                <Title style={styles.radioTitle}>📱 Termux محلي</Title>
                <Paragraph style={styles.radioDescription}>
                  تشغيل البوت على هاتفك باستخدام Termux
                </Paragraph>
              </View>
            </View>

            <View style={styles.radioOption}>
              <RadioButton
                value="cloud"
                status={deploymentMode === 'cloud' ? 'checked' : 'unchecked'}
                onPress={() => setDeploymentMode('cloud')}
              />
              <View style={styles.radioLabel}>
                <Title style={styles.radioTitle}>🌐 خادم سحابي</Title>
                <Paragraph style={styles.radioDescription}>
                  تشغيل البوت على خادم سحابي عبر SSH (24/7)
                </Paragraph>
              </View>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* إعدادات SSH */}
      {deploymentMode === 'cloud' && (
        <>
          <Card style={styles.card}>
            <Card.Content>
              <Title style={styles.cardTitle}>🔧 إعدادات الخادم السحابي</Title>
              <Paragraph style={styles.description}>
                أدخل معلومات الاتصال بخادمك السحابي
              </Paragraph>

              <TextInput
                label="عنوان الخادم (IP أو Domain)"
                value={sshConfig.host}
                onChangeText={(text) => setSshConfig({...sshConfig, host: text})}
                style={styles.input}
                placeholder="example.com أو 192.168.1.100"
                left={<TextInput.Icon icon="server" />}
              />

              <TextInput
                label="البورت"
                value={sshConfig.port}
                onChangeText={(text) => setSshConfig({...sshConfig, port: text})}
                style={styles.input}
                keyboardType="numeric"
                placeholder="22"
                left={<TextInput.Icon icon="network" />}
              />

              <TextInput
                label="اسم المستخدم"
                value={sshConfig.username}
                onChangeText={(text) => setSshConfig({...sshConfig, username: text})}
                style={styles.input}
                placeholder="root أو ubuntu"
                left={<TextInput.Icon icon="account" />}
              />

              <Divider style={styles.divider} />

              <View style={styles.authSection}>
                <Title style={styles.sectionTitle}>🔐 طريقة المصادقة</Title>
                
                <View style={styles.switchContainer}>
                  <Paragraph>استخدام مفتاح خاص (Private Key)</Paragraph>
                  <Switch
                    value={sshConfig.usePrivateKey}
                    onValueChange={(value) => setSshConfig({...sshConfig, usePrivateKey: value})}
                  />
                </View>

                {sshConfig.usePrivateKey ? (
                  <TextInput
                    label="المفتاح الخاص (Private Key)"
                    value={sshConfig.privateKey}
                    onChangeText={(text) => setSshConfig({...sshConfig, privateKey: text})}
                    style={styles.input}
                    multiline
                    numberOfLines={4}
                    placeholder="-----BEGIN PRIVATE KEY-----"
                    left={<TextInput.Icon icon="key" />}
                  />
                ) : (
                  <TextInput
                    label="كلمة المرور"
                    value={sshConfig.password}
                    onChangeText={(text) => setSshConfig({...sshConfig, password: text})}
                    style={styles.input}
                    secureTextEntry
                    placeholder="كلمة مرور الخادم"
                    left={<TextInput.Icon icon="lock" />}
                  />
                )}
              </View>

              <View style={styles.buttonContainer}>
                <Button
                  mode="outlined"
                  onPress={handleTestConnection}
                  loading={testingConnection}
                  disabled={testingConnection}
                  style={styles.testButton}
                  icon="connection"
                >
                  اختبار الاتصال
                </Button>

                <Button
                  mode="contained"
                  onPress={handleSaveConfig}
                  loading={loading}
                  disabled={loading}
                  style={styles.saveButton}
                  icon="content-save"
                >
                  حفظ الإعدادات
                </Button>
              </View>

              {connectionStatus !== null && (
                <Surface style={[
                  styles.statusCard,
                  { backgroundColor: connectionStatus ? '#e8f5e8' : '#ffeaea' }
                ]}>
                  <View style={styles.statusContent}>
                    <IconButton
                      icon={connectionStatus ? "check-circle" : "alert-circle"}
                      iconColor={connectionStatus ? "#4caf50" : "#f44336"}
                      size={24}
                    />
                    <Paragraph style={[
                      styles.statusText,
                      { color: connectionStatus ? "#2e7d32" : "#d32f2f" }
                    ]}>
                      {connectionStatus 
                        ? "✅ الاتصال ناجح! الخادم متاح ويمكن الوصول إليه"
                        : "❌ فشل الاتصال! تحقق من الإعدادات"
                      }
                    </Paragraph>
                  </View>
                </Surface>
              )}
            </Card.Content>
          </Card>

          <Card style={styles.card}>
            <Card.Content>
              <Title style={styles.cardTitle}>💡 نصائح مهمة</Title>
              
              <View style={styles.tipContainer}>
                <IconButton icon="information" iconColor="#2196f3" size={20} />
                <Paragraph style={styles.tipText}>
                  تأكد من أن الخادم يدعم Python 3 و pip
                </Paragraph>
              </View>

              <View style={styles.tipContainer}>
                <IconButton icon="security" iconColor="#ff9800" size={20} />
                <Paragraph style={styles.tipText}>
                  استخدم مفتاح SSH بدلاً من كلمة المرور للأمان
                </Paragraph>
              </View>

              <View style={styles.tipContainer}>
                <IconButton icon="cloud" iconColor="#4caf50" size={20} />
                <Paragraph style={styles.tipText}>
                  الخوادم السحابية توفر تشغيل مستمر 24/7
                </Paragraph>
              </View>

              <View style={styles.tipContainer}>
                <IconButton icon="currency-usd" iconColor="#9c27b0" size={20} />
                <Paragraph style={styles.tipText}>
                  يمكنك استخدام خوادم مجانية مثل Oracle Cloud أو AWS Free Tier
                </Paragraph>
              </View>
            </Card.Content>
          </Card>
        </>
      )}

      {/* معلومات Termux */}
      {deploymentMode === 'termux' && (
        <Card style={styles.card}>
          <Card.Content>
            <Title style={styles.cardTitle}>📱 معلومات Termux</Title>
            
            <View style={styles.tipContainer}>
              <IconButton icon="download" iconColor="#4caf50" size={20} />
              <Paragraph style={styles.tipText}>
                يجب تثبيت Termux من F-Droid أو GitHub
              </Paragraph>
            </View>

            <View style={styles.tipContainer}>
              <IconButton icon="battery" iconColor="#ff9800" size={20} />
              <Paragraph style={styles.tipText}>
                تأكد من إبقاء الهاتف متصلاً بالشاحن
              </Paragraph>
            </View>

            <View style={styles.tipContainer}>
              <IconButton icon="wifi" iconColor="#2196f3" size={20} />
              <Paragraph style={styles.tipText}>
                يحتاج اتصال إنترنت مستقر ومستمر
              </Paragraph>
            </View>

            <View style={styles.tipContainer}>
              <IconButton icon="sleep" iconColor="#9c27b0" size={20} />
              <Paragraph style={styles.tipText}>
                قم بتعطيل وضع السكون للهاتف لضمان التشغيل المستمر
              </Paragraph>
            </View>
          </Card.Content>
        </Card>
      )}

      {/* أزرار الإجراءات */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>⚙️ إجراءات</Title>
          
          <Button
            mode="outlined"
            onPress={handleResetSettings}
            style={styles.resetButton}
            icon="refresh"
            textColor="#f44336"
          >
            إعادة تعيين جميع الإعدادات
          </Button>
        </Card.Content>
      </Card>

      {/* معلومات المطور */}
      <Card style={styles.card}>
        <Card.Content>
          <Title style={styles.cardTitle}>👨‍💻 معلومات التطبيق</Title>
          <Paragraph style={styles.developerText}>
            المطور: Mohamad Zalaf ©2025
          </Paragraph>
          <Paragraph style={styles.versionText}>
            الإصدار: 1.0.0
          </Paragraph>
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 16,
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
  },
  radioContainer: {
    marginTop: 8,
  },
  radioOption: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  radioLabel: {
    flex: 1,
    marginLeft: 8,
  },
  radioTitle: {
    fontSize: 16,
    marginBottom: 4,
  },
  radioDescription: {
    fontSize: 12,
    color: '#666',
  },
  input: {
    marginBottom: 12,
  },
  divider: {
    marginVertical: 16,
  },
  authSection: {
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 16,
    marginBottom: 12,
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 16,
  },
  testButton: {
    flex: 1,
    marginRight: 8,
  },
  saveButton: {
    flex: 1,
    marginLeft: 8,
  },
  statusCard: {
    marginTop: 16,
    padding: 12,
    borderRadius: 8,
  },
  statusContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusText: {
    flex: 1,
    marginLeft: 8,
    fontSize: 14,
  },
  tipContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  tipText: {
    flex: 1,
    fontSize: 14,
    marginLeft: 8,
  },
  resetButton: {
    marginTop: 8,
    borderColor: '#f44336',
  },
  developerText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#2196f3',
    marginBottom: 4,
  },
  versionText: {
    fontSize: 12,
    color: '#666',
  },
});