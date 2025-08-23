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
  List,
  Divider,
  FAB,
  Modal,
  Portal,
  Chip,
} from 'react-native-paper';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export default function ProxyManagementScreen() {
  const [proxyTypes, setProxyTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentProxy, setCurrentProxy] = useState(null);

  // بيانات النموذج
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');

  useEffect(() => {
    loadProxyTypes();
  }, []);

  const loadProxyTypes = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/proxy-types`);
      setProxyTypes(response.data);
    } catch (error) {
      console.error('خطأ في تحميل أنواع البروكسي:', error);
      Alert.alert('خطأ', 'فشل في تحميل أنواع البروكسي');
    }
  };

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    loadProxyTypes().then(() => setRefreshing(false));
  }, []);

  const openAddModal = () => {
    setEditMode(false);
    setCurrentProxy(null);
    setName('');
    setDescription('');
    setPrice('');
    setModalVisible(true);
  };

  const openEditModal = (proxy) => {
    setEditMode(true);
    setCurrentProxy(proxy);
    setName(proxy.name);
    setDescription(proxy.description);
    setPrice(proxy.price.toString());
    setModalVisible(true);
  };

  const closeModal = () => {
    setModalVisible(false);
    setName('');
    setDescription('');
    setPrice('');
    setCurrentProxy(null);
  };

  const handleSave = async () => {
    if (!name.trim() || !description.trim() || !price.trim()) {
      Alert.alert('خطأ', 'يرجى ملء جميع الحقول');
      return;
    }

    const priceValue = parseFloat(price);
    if (isNaN(priceValue) || priceValue <= 0) {
      Alert.alert('خطأ', 'يرجى إدخال سعر صحيح');
      return;
    }

    setLoading(true);
    try {
      const data = {
        name: name.trim(),
        description: description.trim(),
        price: priceValue
      };

      if (editMode) {
        // تعديل (سيتم إضافة API لاحقاً)
        Alert.alert('قريباً', 'سيتم إضافة ميزة التعديل قريباً');
      } else {
        // إضافة جديد
        const response = await axios.post(`${API_BASE_URL}/proxy-types`, data);
        
        if (response.data.success) {
          Alert.alert('نجح', response.data.message || 'تم إضافة نوع البروكسي بنجاح');
          closeModal();
          loadProxyTypes();
        } else {
          Alert.alert('خطأ', 'فشل في إضافة نوع البروكسي');
        }
      }
    } catch (error) {
      console.error('خطأ في الحفظ:', error);
      Alert.alert('خطأ', 'فشل في حفظ البيانات');
    }
    setLoading(false);
  };

  const handleDelete = (proxy) => {
    Alert.alert(
      'تأكيد الحذف',
      `هل أنت متأكد من حذف "${proxy.name}"؟`,
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'حذف',
          style: 'destructive',
          onPress: () => {
            // سيتم إضافة API للحذف لاحقاً
            Alert.alert('قريباً', 'سيتم إضافة ميزة الحذف قريباً');
          }
        }
      ]
    );
  };

  return (
    <View style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* إحصائيات سريعة */}
        <Card style={styles.statsCard}>
          <Card.Content>
            <Title>إحصائيات البروكسيات</Title>
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Paragraph style={styles.statNumber}>{proxyTypes.length}</Paragraph>
                <Paragraph style={styles.statLabel}>إجمالي الأنواع</Paragraph>
              </View>
              <View style={styles.statItem}>
                <Paragraph style={styles.statNumber}>
                  {proxyTypes.filter(p => p.is_active).length}
                </Paragraph>
                <Paragraph style={styles.statLabel}>نشط</Paragraph>
              </View>
              <View style={styles.statItem}>
                <Paragraph style={styles.statNumber}>
                  ${proxyTypes.reduce((sum, p) => sum + (p.is_active ? p.price : 0), 0).toFixed(2)}
                </Paragraph>
                <Paragraph style={styles.statLabel}>متوسط السعر</Paragraph>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* قائمة البروكسيات */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>أنواع البروكسيات المتوفرة</Title>
            
            {proxyTypes.length === 0 ? (
              <View style={styles.emptyState}>
                <Paragraph style={styles.emptyText}>
                  لا توجد أنواع بروكسي مضافة بعد
                </Paragraph>
                <Button
                  mode="contained"
                  onPress={openAddModal}
                  icon="plus"
                  style={styles.emptyButton}
                >
                  إضافة أول نوع بروكسي
                </Button>
              </View>
            ) : (
              proxyTypes.map((proxy, index) => (
                <View key={proxy.id}>
                  <List.Item
                    title={proxy.name}
                    description={proxy.description}
                    left={(props) => (
                      <List.Icon {...props} icon="dns" />
                    )}
                    right={(props) => (
                      <View style={styles.listRight}>
                        <Chip
                          style={[
                            styles.priceChip,
                            { backgroundColor: proxy.is_active ? '#4CAF50' : '#FFC107' }
                          ]}
                          textStyle={{ color: 'white', fontWeight: 'bold' }}
                        >
                          ${proxy.price}
                        </Chip>
                        <Button
                          mode="text"
                          onPress={() => openEditModal(proxy)}
                          icon="pencil"
                          compact
                        >
                          تعديل
                        </Button>
                        <Button
                          mode="text"
                          onPress={() => handleDelete(proxy)}
                          icon="delete"
                          textColor="#F44336"
                          compact
                        >
                          حذف
                        </Button>
                      </View>
                    )}
                    style={[
                      styles.listItem,
                      { opacity: proxy.is_active ? 1 : 0.7 }
                    ]}
                  />
                  {index < proxyTypes.length - 1 && <Divider />}
                </View>
              ))
            )}
          </Card.Content>
        </Card>

        {/* معلومات إضافية */}
        <Card style={styles.card}>
          <Card.Content>
            <Title>نصائح مهمة</Title>
            <List.Item
              title="أسعار تنافسية"
              description="تأكد من وضع أسعار تنافسية لجذب المزيد من العملاء"
              left={(props) => <List.Icon {...props} icon="currency-usd" />}
            />
            <Divider />
            <List.Item
              title="وصف واضح"
              description="اكتب وصفاً واضحاً ومفصلاً لكل نوع بروكسي"
              left={(props) => <List.Icon {...props} icon="text-box" />}
            />
            <Divider />
            <List.Item
              title="تحديث منتظم"
              description="راجع وحدث أنواع البروكسيات بانتظام"
              left={(props) => <List.Icon {...props} icon="update" />}
            />
          </Card.Content>
        </Card>
      </ScrollView>

      {/* زر الإضافة العائم */}
      {proxyTypes.length > 0 && (
        <FAB
          style={styles.fab}
          icon="plus"
          onPress={openAddModal}
          label="إضافة بروكسي"
        />
      )}

      {/* نموذج الإضافة/التعديل */}
      <Portal>
        <Modal
          visible={modalVisible}
          onDismiss={closeModal}
          contentContainerStyle={styles.modal}
        >
          <Title>{editMode ? 'تعديل نوع البروكسي' : 'إضافة نوع بروكسي جديد'}</Title>
          
          <TextInput
            label="اسم نوع البروكسي"
            value={name}
            onChangeText={setName}
            mode="outlined"
            style={styles.input}
            placeholder="مثال: SOCKS5"
          />

          <TextInput
            label="الوصف"
            value={description}
            onChangeText={setDescription}
            mode="outlined"
            multiline
            numberOfLines={3}
            style={styles.input}
            placeholder="وصف مفصل عن نوع البروكسي..."
          />

          <TextInput
            label="السعر بالدولار"
            value={price}
            onChangeText={setPrice}
            mode="outlined"
            keyboardType="numeric"
            style={styles.input}
            placeholder="5.00"
            left={<TextInput.Icon icon="currency-usd" />}
          />

          <View style={styles.modalButtons}>
            <Button
              mode="outlined"
              onPress={closeModal}
              style={styles.modalButton}
            >
              إلغاء
            </Button>
            <Button
              mode="contained"
              onPress={handleSave}
              loading={loading}
              style={styles.modalButton}
            >
              {editMode ? 'حفظ التعديل' : 'إضافة'}
            </Button>
          </View>
        </Modal>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  statsCard: {
    margin: 16,
    marginBottom: 8,
    elevation: 4,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2196F3',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
  },
  card: {
    margin: 16,
    marginTop: 8,
    elevation: 4,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyText: {
    color: '#666',
    marginBottom: 16,
    textAlign: 'center',
  },
  emptyButton: {
    backgroundColor: '#2196F3',
  },
  listItem: {
    paddingVertical: 8,
  },
  listRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  priceChip: {
    marginRight: 8,
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
    backgroundColor: '#2196F3',
  },
  modal: {
    backgroundColor: 'white',
    padding: 24,
    margin: 20,
    borderRadius: 8,
  },
  input: {
    marginBottom: 16,
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