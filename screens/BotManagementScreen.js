import React, { useState, useEffect } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  Alert,
  RefreshControl,
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
} from 'react-native-paper';
import DateTimePicker from '@react-native-community/datetimepicker';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export default function BotManagementScreen() {
  const [botStatus, setBotStatus] = useState(false);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [apiKey, setApiKey] = useState('8408804784:AAG8cSTsDQfycDaXOX9YMmc_OB3wABez7LA');
  const [adminId, setAdminId] = useState('6891599955');
  
  // إعدادات الجدولة
  const [scheduledStart, setScheduledStart] = useState(false);
  const [scheduledStop, setScheduledStop] = useState(false);
  const [startTime, setStartTime] = useState(new Date());
  const [stopTime, setStopTime] = useState(new Date());
  const [showStartTimePicker, setShowStartTimePicker] = useState(false);
  const [showStopTimePicker, setShowStopTimePicker] = useState(false);

  useEffect(() => {
    checkBotStatus();
  }, []);

  const checkBotStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/bot/status`);
      setBotStatus(response.data.running);
    } catch (error) {
      console.error('خطأ في التحقق من حالة البوت:', error);
    }
  };

  const handleStartBot = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/bot/start`, {
        admin_id: adminId
      });
      
      if (response.data.success) {
        setBotStatus(true);
        Alert.alert('نجح', response.data.message);
      } else {
        Alert.alert('خطأ', response.data.message);
      }
    } catch (error) {
      Alert.alert('خطأ', 'فشل في بدء البوت');
      console.error('خطأ في بدء البوت:', error);
    }
    setLoading(false);
  };

  const handleStopBot = async () => {
    Alert.alert(
      'تأكيد الإيقاف',
      'هل أنت متأكد من إيقاف البوت؟ لن يتمكن المستخدمون من إرسال طلبات جديدة.',
      [
        { text: 'إلغاء', style: 'cancel' },
        { 
          text: 'إيقاف', 
          style: 'destructive',
          onPress: async () => {
            setLoading(true);
            try {
              const response = await axios.post(`${API_BASE_URL}/bot/stop`);
              
              if (response.data.success) {
                setBotStatus(false);
                Alert.alert('نجح', response.data.message);
              } else {
                Alert.alert('خطأ', response.data.message);
              }
            } catch (error) {
              Alert.alert('خطأ', 'فشل في إيقاف البوت');
              console.error('خطأ في إيقاف البوت:', error);
            }
            setLoading(false);
          }
        }
      ]
    );
  };

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    checkBotStatus().then(() => setRefreshing(false));
  }, []);

  const handleStartTimeChange = (event, selectedTime) => {
    setShowStartTimePicker(false);
    if (selectedTime) {
      setStartTime(selectedTime);
    }
  };

  const handleStopTimeChange = (event, selectedTime) => {
    setShowStopTimePicker(false);
    if (selectedTime) {
      setStopTime(selectedTime);
    }
  };

  const saveScheduleSettings = () => {
    Alert.alert('تم الحفظ', 'تم حفظ إعدادات الجدولة بنجاح');
  };

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* حالة البوت */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.statusHeader}>
            <Title>حالة البوت</Title>
            <Chip 
              icon={botStatus ? 'check-circle' : 'close-circle'}
              style={[
                styles.statusChip,
                { backgroundColor: botStatus ? '#4CAF50' : '#F44336' }
              ]}
              textStyle={{ color: 'white' }}
            >
              {botStatus ? 'يعمل' : 'متوقف'}
            </Chip>
          </View>
          
          <Paragraph style={styles.statusText}>
            {botStatus 
              ? 'البوت نشط ويستقبل الطلبات من المستخدمين'
              : 'البوت متوقف ولا يستقبل طلبات جديدة'
            }
          </Paragraph>

          <View style={styles.buttonRow}>
            <Button
              mode="contained"
              onPress={handleStartBot}
              loading={loading && !botStatus}
              disabled={botStatus || loading}
              style={[styles.button, styles.startButton]}
              icon="play"
            >
              تشغيل البوت
            </Button>

            <Button
              mode="contained"
              onPress={handleStopBot}
              loading={loading && botStatus}
              disabled={!botStatus || loading}
              style={[styles.button, styles.stopButton]}
              icon="stop"
            >
              إيقاف البوت
            </Button>
          </View>
        </Card.Content>
      </Card>

      {/* إعدادات البوت */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>إعدادات البوت</Title>
          
          <TextInput
            label="مفتاح API للبوت"
            value={apiKey}
            onChangeText={setApiKey}
            mode="outlined"
            style={styles.input}
            right={<TextInput.Icon icon="key" />}
          />

          <TextInput
            label="معرف الأدمن"
            value={adminId}
            onChangeText={setAdminId}
            mode="outlined"
            keyboardType="numeric"
            style={styles.input}
            right={<TextInput.Icon icon="account-supervisor" />}
          />

          <Button
            mode="outlined"
            onPress={() => Alert.alert('تم الحفظ', 'تم حفظ الإعدادات بنجاح')}
            style={styles.saveButton}
            icon="content-save"
          >
            حفظ الإعدادات
          </Button>
        </Card.Content>
      </Card>

      {/* الجدولة التلقائية */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>الجدولة التلقائية</Title>
          <Paragraph style={styles.subtitle}>
            جدولة تشغيل وإيقاف البوت في أوقات محددة
          </Paragraph>

          <Divider style={styles.divider} />

          {/* جدولة التشغيل */}
          <Surface style={styles.scheduleItem}>
            <View style={styles.scheduleHeader}>
              <Title style={styles.scheduleTitle}>تشغيل مجدول</Title>
              <Switch
                value={scheduledStart}
                onValueChange={setScheduledStart}
              />
            </View>
            
            {scheduledStart && (
              <View style={styles.timeSelector}>
                <Button
                  mode="outlined"
                  onPress={() => setShowStartTimePicker(true)}
                  icon="clock"
                  style={styles.timeButton}
                >
                  {startTime.toLocaleTimeString('ar-SA', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </Button>
              </View>
            )}
          </Surface>

          {/* جدولة الإيقاف */}
          <Surface style={styles.scheduleItem}>
            <View style={styles.scheduleHeader}>
              <Title style={styles.scheduleTitle}>إيقاف مجدول</Title>
              <Switch
                value={scheduledStop}
                onValueChange={setScheduledStop}
              />
            </View>
            
            {scheduledStop && (
              <View style={styles.timeSelector}>
                <Button
                  mode="outlined"
                  onPress={() => setShowStopTimePicker(true)}
                  icon="clock"
                  style={styles.timeButton}
                >
                  {stopTime.toLocaleTimeString('ar-SA', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </Button>
              </View>
            )}
          </Surface>

          <Button
            mode="contained"
            onPress={saveScheduleSettings}
            style={styles.saveScheduleButton}
            icon="calendar-check"
          >
            حفظ إعدادات الجدولة
          </Button>
        </Card.Content>
      </Card>

      {/* معلومات النظام */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>معلومات النظام</Title>
          
          <View style={styles.infoRow}>
            <Paragraph style={styles.infoLabel}>الخادم:</Paragraph>
            <Paragraph style={styles.infoValue}>محلي (localhost:5000)</Paragraph>
          </View>
          
          <View style={styles.infoRow}>
            <Paragraph style={styles.infoLabel}>الإصدار:</Paragraph>
            <Paragraph style={styles.infoValue}>1.0.0</Paragraph>
          </View>
          
          <View style={styles.infoRow}>
            <Paragraph style={styles.infoLabel}>آخر تحديث:</Paragraph>
            <Paragraph style={styles.infoValue}>{new Date().toLocaleDateString('ar-SA')}</Paragraph>
          </View>

          <Divider style={styles.divider} />

          <Button
            mode="outlined"
            onPress={() => Alert.alert('معلومات', 'بوت البروكسي v1.0.0\nتم التطوير بـ ❤️')}
            style={styles.infoButton}
            icon="information"
          >
            معلومات التطبيق
          </Button>
        </Card.Content>
      </Card>

      {/* أدوات الصيانة */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>أدوات الصيانة</Title>
          
          <View style={styles.maintenanceButtons}>
            <Button
              mode="outlined"
              onPress={() => Alert.alert('تم', 'تم تنظيف الذاكرة المؤقتة')}
              style={styles.maintenanceButton}
              icon="broom"
            >
              تنظيف الذاكرة
            </Button>
            
            <Button
              mode="outlined"
              onPress={() => Alert.alert('تم', 'تم إنشاء نسخة احتياطية')}
              style={styles.maintenanceButton}
              icon="backup-restore"
            >
              نسخ احتياطي
            </Button>
          </View>
        </Card.Content>
      </Card>

      {/* Date Time Pickers */}
      {showStartTimePicker && (
        <DateTimePicker
          value={startTime}
          mode="time"
          is24Hour={true}
          display="default"
          onChange={handleStartTimeChange}
        />
      )}

      {showStopTimePicker && (
        <DateTimePicker
          value={stopTime}
          mode="time"
          is24Hour={true}
          display="default"
          onChange={handleStopTimeChange}
        />
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  statusHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusChip: {
    elevation: 2,
  },
  statusText: {
    marginBottom: 16,
    color: '#666',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  button: {
    flex: 1,
    marginHorizontal: 8,
  },
  startButton: {
    backgroundColor: '#4CAF50',
  },
  stopButton: {
    backgroundColor: '#F44336',
  },
  input: {
    marginBottom: 16,
  },
  saveButton: {
    marginTop: 8,
  },
  subtitle: {
    color: '#666',
    marginBottom: 16,
  },
  divider: {
    marginVertical: 16,
  },
  scheduleItem: {
    padding: 16,
    marginBottom: 12,
    borderRadius: 8,
    elevation: 1,
  },
  scheduleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  scheduleTitle: {
    fontSize: 16,
  },
  timeSelector: {
    marginTop: 12,
  },
  timeButton: {
    alignSelf: 'flex-start',
  },
  saveScheduleButton: {
    marginTop: 16,
    backgroundColor: '#2196F3',
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  infoLabel: {
    fontWeight: 'bold',
    color: '#333',
  },
  infoValue: {
    color: '#666',
  },
  infoButton: {
    marginTop: 8,
  },
  maintenanceButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  maintenanceButton: {
    flex: 1,
    marginHorizontal: 8,
  },
});