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
  Chip,
  Surface,
} from 'react-native-paper';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export default function PaymentManagementScreen() {
  const [totalEarnings, setTotalEarnings] = useState(0);
  const [proxyTypes, setProxyTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [editingPrices, setEditingPrices] = useState(false);
  const [tempPrices, setTempPrices] = useState({});

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [earningsResponse, proxyTypesResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/earnings`),
        axios.get(`${API_BASE_URL}/proxy-types`)
      ]);
      
      setTotalEarnings(earningsResponse.data.total_earnings);
      setProxyTypes(proxyTypesResponse.data);
      
      // إعداد الأسعار المؤقتة للتعديل
      const prices = {};
      proxyTypesResponse.data.forEach(proxy => {
        prices[proxy.id] = proxy.price.toString();
      });
      setTempPrices(prices);
    } catch (error) {
      console.error('خطأ في تحميل البيانات:', error);
      Alert.alert('خطأ', 'فشل في تحميل بيانات المدفوعات');
    }
  };

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    loadData().then(() => setRefreshing(false));
  }, []);

  const handleEditPrices = () => {
    setEditingPrices(true);
  };

  const handleSavePrices = () => {
    Alert.alert(
      'تأكيد التحديث',
      'هل أنت متأكد من تحديث الأسعار؟',
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'تحديث',
          onPress: async () => {
            // هنا يمكن إضافة API لتحديث الأسعار
            Alert.alert('قريباً', 'سيتم إضافة ميزة تحديث الأسعار قريباً');
            setEditingPrices(false);
          }
        }
      ]
    );
  };

  const handleCancelEdit = () => {
    // إعادة تعيين الأسعار المؤقتة
    const prices = {};
    proxyTypes.forEach(proxy => {
      prices[proxy.id] = proxy.price.toString();
    });
    setTempPrices(prices);
    setEditingPrices(false);
  };

  const updateTempPrice = (proxyId, newPrice) => {
    setTempPrices(prev => ({
      ...prev,
      [proxyId]: newPrice
    }));
  };

  const calculateMonthlyProjection = () => {
    // حساب تقديري للأرباح الشهرية بناءً على متوسط الطلبات
    const avgOrdersPerDay = 5; // متوسط تقديري
    const avgPricePerOrder = proxyTypes.reduce((sum, proxy) => sum + proxy.price, 0) / proxyTypes.length || 0;
    return (avgOrdersPerDay * avgPricePerOrder * 30).toFixed(2);
  };

  const getEarningsGrowth = () => {
    // حساب تقديري لنمو الأرباح (سيتم تحسينه لاحقاً)
    return '+12.5%';
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* إحصائيات الأرباح */}
      <Card style={styles.earningsCard}>
        <Card.Content>
          <Title>إجمالي الأرباح</Title>
          <View style={styles.earningsHeader}>
            <Paragraph style={styles.earningsAmount}>
              ${totalEarnings.toFixed(2)}
            </Paragraph>
            <Chip
              icon="trending-up"
              style={styles.growthChip}
              textStyle={{ color: 'white' }}
            >
              {getEarningsGrowth()}
            </Chip>
          </View>
          
          <View style={styles.earningsStats}>
            <View style={styles.statItem}>
              <Paragraph style={styles.statValue}>
                ${calculateMonthlyProjection()}
              </Paragraph>
              <Paragraph style={styles.statLabel}>توقع شهري</Paragraph>
            </View>
            <View style={styles.statItem}>
              <Paragraph style={styles.statValue}>
                ${(totalEarnings / Math.max(proxyTypes.length, 1)).toFixed(2)}
              </Paragraph>
              <Paragraph style={styles.statLabel}>متوسط لكل نوع</Paragraph>
            </View>
            <View style={styles.statItem}>
              <Paragraph style={styles.statValue}>
                {proxyTypes.filter(p => p.is_active).length}
              </Paragraph>
              <Paragraph style={styles.statLabel}>أنواع نشطة</Paragraph>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* إدارة الأسعار */}
      <Card style={styles.card}>
        <Card.Content>
          <View style={styles.pricesHeader}>
            <Title>إدارة الأسعار</Title>
            {!editingPrices ? (
              <Button
                mode="outlined"
                onPress={handleEditPrices}
                icon="pencil"
                compact
              >
                تعديل
              </Button>
            ) : (
              <View style={styles.editButtons}>
                <Button
                  mode="outlined"
                  onPress={handleCancelEdit}
                  compact
                  style={styles.editButton}
                >
                  إلغاء
                </Button>
                <Button
                  mode="contained"
                  onPress={handleSavePrices}
                  icon="check"
                  compact
                  style={styles.editButton}
                >
                  حفظ
                </Button>
              </View>
            )}
          </View>

          {proxyTypes.length === 0 ? (
            <View style={styles.emptyState}>
              <Paragraph style={styles.emptyText}>
                لا توجد أنواع بروكسي مضافة بعد
              </Paragraph>
            </View>
          ) : (
            proxyTypes.map((proxy, index) => (
              <View key={proxy.id}>
                <View style={styles.priceItem}>
                  <View style={styles.proxyInfo}>
                    <Title style={styles.proxyName}>{proxy.name}</Title>
                    <Paragraph style={styles.proxyDescription}>
                      {proxy.description}
                    </Paragraph>
                  </View>
                  
                  <View style={styles.priceSection}>
                    {editingPrices ? (
                      <TextInput
                        value={tempPrices[proxy.id] || ''}
                        onChangeText={(text) => updateTempPrice(proxy.id, text)}
                        mode="outlined"
                        keyboardType="numeric"
                        style={styles.priceInput}
                        left={<TextInput.Icon icon="currency-usd" />}
                      />
                    ) : (
                      <View style={styles.priceDisplay}>
                        <Paragraph style={styles.priceText}>
                          ${proxy.price}
                        </Paragraph>
                        <Chip
                          style={[
                            styles.statusChip,
                            { backgroundColor: proxy.is_active ? '#4CAF50' : '#FFC107' }
                          ]}
                          textStyle={{ color: 'white', fontSize: 10 }}
                        >
                          {proxy.is_active ? 'نشط' : 'معطل'}
                        </Chip>
                      </View>
                    )}
                  </View>
                </View>
                {index < proxyTypes.length - 1 && <Divider />}
              </View>
            ))
          )}
        </Card.Content>
      </Card>

      {/* تحليل الأرباح */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>تحليل الأرباح</Title>
          
          <Surface style={styles.analysisItem}>
            <List.Item
              title="أعلى نوع ربحية"
              description={proxyTypes.length > 0 ? 
                `${proxyTypes.reduce((max, proxy) => proxy.price > max.price ? proxy : max, proxyTypes[0])?.name} - $${proxyTypes.reduce((max, proxy) => proxy.price > max.price ? proxy : max, proxyTypes[0])?.price}` 
                : 'لا توجد بيانات'}
              left={(props) => <List.Icon {...props} icon="trophy" />}
            />
          </Surface>

          <Surface style={styles.analysisItem}>
            <List.Item
              title="متوسط سعر البروكسي"
              description={proxyTypes.length > 0 ? 
                `$${(proxyTypes.reduce((sum, proxy) => sum + proxy.price, 0) / proxyTypes.length).toFixed(2)}` 
                : '$0.00'}
              left={(props) => <List.Icon {...props} icon="calculator" />}
            />
          </Surface>

          <Surface style={styles.analysisItem}>
            <List.Item
              title="إجمالي الأنواع النشطة"
              description={`${proxyTypes.filter(p => p.is_active).length} من أصل ${proxyTypes.length}`}
              left={(props) => <List.Icon {...props} icon="chart-line" />}
            />
          </Surface>
        </Card.Content>
      </Card>

      {/* أدوات مالية */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>أدوات مالية</Title>
          
          <View style={styles.toolsGrid}>
            <Button
              mode="outlined"
              onPress={() => Alert.alert('قريباً', 'سيتم إضافة تقرير الأرباح الشهرية قريباً')}
              icon="file-chart"
              style={styles.toolButton}
            >
              تقرير شهري
            </Button>
            
            <Button
              mode="outlined"
              onPress={() => Alert.alert('قريباً', 'سيتم إضافة تصدير البيانات قريباً')}
              icon="export"
              style={styles.toolButton}
            >
              تصدير البيانات
            </Button>
          </View>

          <View style={styles.toolsGrid}>
            <Button
              mode="outlined"
              onPress={() => Alert.alert('قريباً', 'سيتم إضافة حاسبة الضرائب قريباً')}
              icon="calculator-variant"
              style={styles.toolButton}
            >
              حاسبة الضرائب
            </Button>
            
            <Button
              mode="outlined"
              onPress={() => Alert.alert('قريباً', 'سيتم إضافة الإحصائيات المتقدمة قريباً')}
              icon="chart-box"
              style={styles.toolButton}
            >
              إحصائيات متقدمة
            </Button>
          </View>
        </Card.Content>
      </Card>

      {/* نصائح مالية */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>نصائح مالية</Title>
          
          <List.Item
            title="مراجعة الأسعار"
            description="راجع أسعار البروكسيات شهرياً لضمان المنافسة"
            left={(props) => <List.Icon {...props} icon="cash-multiple" />}
          />
          <Divider />
          
          <List.Item
            title="تتبع الاتجاهات"
            description="راقب اتجاهات السوق لتحديد أفضل الأسعار"
            left={(props) => <List.Icon {...props} icon="trending-up" />}
          />
          <Divider />
          
          <List.Item
            title="تنويع الأنواع"
            description="قدم أنواع مختلفة من البروكسيات لزيادة الأرباح"
            left={(props) => <List.Icon {...props} icon="diversify" />}
          />
        </Card.Content>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  earningsCard: {
    marginBottom: 16,
    elevation: 4,
    backgroundColor: '#2196F3',
  },
  earningsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  earningsAmount: {
    fontSize: 32,
    fontWeight: 'bold',
    color: 'white',
  },
  growthChip: {
    backgroundColor: '#4CAF50',
  },
  earningsStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
  },
  statLabel: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.8)',
  },
  card: {
    marginBottom: 16,
    elevation: 4,
  },
  pricesHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  editButtons: {
    flexDirection: 'row',
  },
  editButton: {
    marginLeft: 8,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyText: {
    color: '#666',
    textAlign: 'center',
  },
  priceItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
  },
  proxyInfo: {
    flex: 1,
  },
  proxyName: {
    fontSize: 16,
    marginBottom: 4,
  },
  proxyDescription: {
    color: '#666',
    fontSize: 12,
  },
  priceSection: {
    alignItems: 'flex-end',
  },
  priceInput: {
    width: 120,
    height: 40,
  },
  priceDisplay: {
    alignItems: 'center',
  },
  priceText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2196F3',
    marginBottom: 4,
  },
  statusChip: {
    elevation: 1,
  },
  analysisItem: {
    marginBottom: 8,
    elevation: 1,
    borderRadius: 8,
  },
  toolsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 12,
  },
  toolButton: {
    flex: 1,
    marginHorizontal: 4,
  },
});