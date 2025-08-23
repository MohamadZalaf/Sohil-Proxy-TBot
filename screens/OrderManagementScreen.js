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
  List,
  Divider,
  Chip,
  Modal,
  Portal,
  TextInput,
  SegmentedButtons,
} from 'react-native-paper';
import DateTimePicker from '@react-native-community/datetimepicker';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export default function OrderManagementScreen() {
  const [activeTab, setActiveTab] = useState('pending');
  const [pendingOrders, setPendingOrders] = useState([]);
  const [completedOrders, setCompletedOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [processModalVisible, setProcessModalVisible] = useState(false);
  const [currentOrder, setCurrentOrder] = useState(null);

  // بيانات معالجة الطلب
  const [proxyHost, setProxyHost] = useState('');
  const [proxyPort, setProxyPort] = useState('');
  const [proxyUsername, setProxyUsername] = useState('');
  const [proxyPassword, setProxyPassword] = useState('');
  const [proxyCountry, setProxyCountry] = useState('');
  const [proxyRegion, setProxyRegion] = useState('');
  const [expiryDate, setExpiryDate] = useState(new Date());
  const [expiryTime, setExpiryTime] = useState(new Date());
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      const [pendingResponse, completedResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/orders/pending`),
        axios.get(`${API_BASE_URL}/orders/completed`)
      ]);
      
      setPendingOrders(pendingResponse.data);
      setCompletedOrders(completedResponse.data);
    } catch (error) {
      console.error('خطأ في تحميل الطلبات:', error);
      Alert.alert('خطأ', 'فشل في تحميل الطلبات');
    }
  };

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    loadOrders().then(() => setRefreshing(false));
  }, []);

  const openProcessModal = (order) => {
    setCurrentOrder(order);
    // تعيين قيم افتراضية
    setProxyHost('');
    setProxyPort('8080');
    setProxyUsername('');
    setProxyPassword('');
    setProxyCountry('');
    setProxyRegion('');
    setExpiryDate(new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)); // 30 يوم من الآن
    setExpiryTime(new Date());
    setProcessModalVisible(true);
  };

  const closeProcessModal = () => {
    setProcessModalVisible(false);
    setCurrentOrder(null);
    // إعادة تعيين القيم
    setProxyHost('');
    setProxyPort('');
    setProxyUsername('');
    setProxyPassword('');
    setProxyCountry('');
    setProxyRegion('');
  };

  const handleProcessOrder = async () => {
    if (!proxyHost || !proxyPort || !proxyUsername || !proxyPassword || !proxyCountry) {
      Alert.alert('خطأ', 'يرجى ملء جميع الحقول المطلوبة');
      return;
    }

    setLoading(true);
    try {
      const proxyInfo = {
        host: proxyHost.trim(),
        port: proxyPort.trim(),
        username: proxyUsername.trim(),
        password: proxyPassword.trim(),
        country: proxyCountry.trim(),
        region: proxyRegion.trim(),
        expiry_date: expiryDate.toLocaleDateString('ar-SA'),
        expiry_time: expiryTime.toLocaleTimeString('ar-SA', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      };

      const response = await axios.post(
        `${API_BASE_URL}/orders/${currentOrder.id}/complete`,
        { proxy_info: proxyInfo }
      );

      if (response.data.success) {
        Alert.alert('نجح', response.data.message);
        closeProcessModal();
        loadOrders();
      } else {
        Alert.alert('خطأ', 'فشل في معالجة الطلب');
      }
    } catch (error) {
      console.error('خطأ في معالجة الطلب:', error);
      Alert.alert('خطأ', 'فشل في معالجة الطلب');
    }
    setLoading(false);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'غير محدد';
    return new Date(dateString).toLocaleDateString('ar-SA');
  };

  const formatTime = (dateString) => {
    if (!dateString) return 'غير محدد';
    return new Date(dateString).toLocaleTimeString('ar-SA', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderOrder = (order, isPending = true) => (
    <Card key={order.id} style={styles.orderCard}>
      <Card.Content>
        <View style={styles.orderHeader}>
          <Title style={styles.orderTitle}>طلب #{order.id}</Title>
          <Chip
            icon={isPending ? 'clock' : 'check-circle'}
            style={[
              styles.statusChip,
              { backgroundColor: isPending ? '#FF9800' : '#4CAF50' }
            ]}
            textStyle={{ color: 'white' }}
          >
            {isPending ? 'معلق' : 'مكتمل'}
          </Chip>
        </View>

        <View style={styles.orderDetails}>
          <Paragraph><strong>المستخدم:</strong> {order.first_name} (@{order.username})</Paragraph>
          <Paragraph><strong>نوع البروكسي:</strong> {order.proxy_name}</Paragraph>
          <Paragraph><strong>السعر:</strong> ${order.price}</Paragraph>
          <Paragraph><strong>تاريخ الطلب:</strong> {formatDate(order.created_at)}</Paragraph>
          {!isPending && order.completed_at && (
            <Paragraph><strong>تاريخ الإكمال:</strong> {formatDate(order.completed_at)}</Paragraph>
          )}
        </View>

        {isPending ? (
          <Button
            mode="contained"
            onPress={() => openProcessModal(order)}
            icon="cog"
            style={styles.processButton}
          >
            معالجة الطلب
          </Button>
        ) : (
          order.proxy_info && (
            <View style={styles.proxyInfo}>
              <Title style={styles.proxyInfoTitle}>معلومات البروكسي المرسل:</Title>
              <Paragraph>🌐 العنوان: {order.proxy_info.host}:{order.proxy_info.port}</Paragraph>
              <Paragraph>🌍 الموقع: {order.proxy_info.country}, {order.proxy_info.region}</Paragraph>
              <Paragraph>📅 انتهاء الصلاحية: {order.proxy_info.expiry_date} {order.proxy_info.expiry_time}</Paragraph>
            </View>
          )
        )}
      </Card.Content>
    </Card>
  );

  const currentOrders = activeTab === 'pending' ? pendingOrders : completedOrders;

  return (
    <View style={styles.container}>
      {/* التبويبات */}
      <Card style={styles.tabCard}>
        <Card.Content>
          <SegmentedButtons
            value={activeTab}
            onValueChange={setActiveTab}
            buttons={[
              {
                value: 'pending',
                label: `معلقة (${pendingOrders.length})`,
                icon: 'clock',
              },
              {
                value: 'completed',
                label: `مكتملة (${completedOrders.length})`,
                icon: 'check-circle',
              },
            ]}
            style={styles.segmentedButtons}
          />
        </Card.Content>
      </Card>

      {/* قائمة الطلبات */}
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {currentOrders.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Card.Content style={styles.emptyState}>
              <Paragraph style={styles.emptyText}>
                {activeTab === 'pending' 
                  ? 'لا توجد طلبات معلقة' 
                  : 'لا توجد طلبات مكتملة'
                }
              </Paragraph>
            </Card.Content>
          </Card>
        ) : (
          currentOrders.map(order => renderOrder(order, activeTab === 'pending'))
        )}
      </ScrollView>

      {/* نموذج معالجة الطلب */}
      <Portal>
        <Modal
          visible={processModalVisible}
          onDismiss={closeProcessModal}
          contentContainerStyle={styles.modal}
        >
          <ScrollView>
            <Title>معالجة الطلب #{currentOrder?.id}</Title>
            
            <Paragraph style={styles.orderInfo}>
              المستخدم: {currentOrder?.first_name} (@{currentOrder?.username})
              {'\n'}نوع البروكسي: {currentOrder?.proxy_name}
              {'\n'}السعر: ${currentOrder?.price}
            </Paragraph>

            <Divider style={styles.divider} />

            <Title style={styles.sectionTitle}>معلومات البروكسي</Title>

            <TextInput
              label="عنوان البروكسي *"
              value={proxyHost}
              onChangeText={setProxyHost}
              mode="outlined"
              style={styles.input}
              placeholder="192.168.1.100"
            />

            <TextInput
              label="البورت *"
              value={proxyPort}
              onChangeText={setProxyPort}
              mode="outlined"
              keyboardType="numeric"
              style={styles.input}
              placeholder="8080"
            />

            <TextInput
              label="اسم المستخدم *"
              value={proxyUsername}
              onChangeText={setProxyUsername}
              mode="outlined"
              style={styles.input}
              placeholder="username"
            />

            <TextInput
              label="كلمة المرور *"
              value={proxyPassword}
              onChangeText={setProxyPassword}
              mode="outlined"
              secureTextEntry
              style={styles.input}
              placeholder="password"
            />

            <TextInput
              label="الدولة *"
              value={proxyCountry}
              onChangeText={setProxyCountry}
              mode="outlined"
              style={styles.input}
              placeholder="United States"
            />

            <TextInput
              label="المنطقة"
              value={proxyRegion}
              onChangeText={setProxyRegion}
              mode="outlined"
              style={styles.input}
              placeholder="New York"
            />

            <Title style={styles.sectionTitle}>تاريخ الانتهاء</Title>

            <View style={styles.dateTimeRow}>
              <Button
                mode="outlined"
                onPress={() => setShowDatePicker(true)}
                icon="calendar"
                style={styles.dateButton}
              >
                {expiryDate.toLocaleDateString('ar-SA')}
              </Button>

              <Button
                mode="outlined"
                onPress={() => setShowTimePicker(true)}
                icon="clock"
                style={styles.timeButton}
              >
                {expiryTime.toLocaleTimeString('ar-SA', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </Button>
            </View>

            <View style={styles.modalButtons}>
              <Button
                mode="outlined"
                onPress={closeProcessModal}
                style={styles.modalButton}
              >
                إلغاء
              </Button>
              <Button
                mode="contained"
                onPress={handleProcessOrder}
                loading={loading}
                style={styles.modalButton}
              >
                إرسال البروكسي
              </Button>
            </View>
          </ScrollView>
        </Modal>
      </Portal>

      {/* Date Time Pickers */}
      {showDatePicker && (
        <DateTimePicker
          value={expiryDate}
          mode="date"
          display="default"
          onChange={(event, selectedDate) => {
            setShowDatePicker(false);
            if (selectedDate) {
              setExpiryDate(selectedDate);
            }
          }}
        />
      )}

      {showTimePicker && (
        <DateTimePicker
          value={expiryTime}
          mode="time"
          is24Hour={true}
          display="default"
          onChange={(event, selectedTime) => {
            setShowTimePicker(false);
            if (selectedTime) {
              setExpiryTime(selectedTime);
            }
          }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  tabCard: {
    margin: 16,
    marginBottom: 8,
    elevation: 4,
  },
  segmentedButtons: {
    marginTop: 8,
  },
  orderCard: {
    margin: 16,
    marginTop: 8,
    elevation: 4,
  },
  orderHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  orderTitle: {
    fontSize: 18,
  },
  statusChip: {
    elevation: 2,
  },
  orderDetails: {
    marginBottom: 16,
  },
  processButton: {
    backgroundColor: '#2196F3',
  },
  proxyInfo: {
    backgroundColor: '#E8F5E8',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
  },
  proxyInfoTitle: {
    fontSize: 14,
    marginBottom: 8,
  },
  emptyCard: {
    margin: 16,
    elevation: 4,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyText: {
    color: '#666',
    textAlign: 'center',
  },
  modal: {
    backgroundColor: 'white',
    padding: 24,
    margin: 20,
    borderRadius: 8,
    maxHeight: '90%',
  },
  orderInfo: {
    backgroundColor: '#f5f5f5',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  divider: {
    marginVertical: 16,
  },
  sectionTitle: {
    fontSize: 16,
    marginBottom: 12,
  },
  input: {
    marginBottom: 16,
  },
  dateTimeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  dateButton: {
    flex: 1,
    marginRight: 8,
  },
  timeButton: {
    flex: 1,
    marginLeft: 8,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 16,
  },
  modalButton: {
    marginLeft: 8,
  },
});