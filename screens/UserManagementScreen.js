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
  Searchbar,
  Avatar,
} from 'react-native-paper';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

export default function UserManagementScreen() {
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadUsers();
  }, []);

  useEffect(() => {
    filterUsers();
  }, [users, searchQuery]);

  const loadUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('خطأ في تحميل المستخدمين:', error);
      Alert.alert('خطأ', 'فشل في تحميل قائمة المستخدمين');
    }
  };

  const filterUsers = () => {
    if (!searchQuery.trim()) {
      setFilteredUsers(users);
    } else {
      const filtered = users.filter(user =>
        user.username?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.first_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.last_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.user_id.toString().includes(searchQuery)
      );
      setFilteredUsers(filtered);
    }
  };

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    loadUsers().then(() => setRefreshing(false));
  }, []);

  const handleBanUser = async (userId, username) => {
    Alert.alert(
      'تأكيد الحظر',
      `هل أنت متأكد من حظر المستخدم "${username}"؟`,
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'حظر',
          style: 'destructive',
          onPress: async () => {
            setLoading(true);
            try {
              const response = await axios.post(`${API_BASE_URL}/users/${userId}/ban`);
              if (response.data.success) {
                Alert.alert('نجح', response.data.message);
                loadUsers();
              } else {
                Alert.alert('خطأ', 'فشل في حظر المستخدم');
              }
            } catch (error) {
              console.error('خطأ في الحظر:', error);
              Alert.alert('خطأ', 'فشل في حظر المستخدم');
            }
            setLoading(false);
          }
        }
      ]
    );
  };

  const handleUnbanUser = async (userId, username) => {
    Alert.alert(
      'تأكيد إلغاء الحظر',
      `هل أنت متأكد من إلغاء حظر المستخدم "${username}"؟`,
      [
        { text: 'إلغاء', style: 'cancel' },
        {
          text: 'إلغاء الحظر',
          onPress: async () => {
            setLoading(true);
            try {
              const response = await axios.post(`${API_BASE_URL}/users/${userId}/unban`);
              if (response.data.success) {
                Alert.alert('نجح', response.data.message);
                loadUsers();
              } else {
                Alert.alert('خطأ', 'فشل في إلغاء حظر المستخدم');
              }
            } catch (error) {
              console.error('خطأ في إلغاء الحظر:', error);
              Alert.alert('خطأ', 'فشل في إلغاء حظر المستخدم');
            }
            setLoading(false);
          }
        }
      ]
    );
  };

  const getInitials = (firstName, lastName) => {
    const first = firstName?.charAt(0)?.toUpperCase() || '';
    const last = lastName?.charAt(0)?.toUpperCase() || '';
    return first + last || '؟';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'غير محدد';
    return new Date(dateString).toLocaleDateString('ar-SA');
  };

  const activeUsers = users.filter(user => !user.is_banned);
  const bannedUsers = users.filter(user => user.is_banned);

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      {/* إحصائيات المستخدمين */}
      <Card style={styles.statsCard}>
        <Card.Content>
          <Title>إحصائيات المستخدمين</Title>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Paragraph style={styles.statNumber}>{users.length}</Paragraph>
              <Paragraph style={styles.statLabel}>إجمالي المستخدمين</Paragraph>
            </View>
            <View style={styles.statItem}>
              <Paragraph style={[styles.statNumber, { color: '#4CAF50' }]}>
                {activeUsers.length}
              </Paragraph>
              <Paragraph style={styles.statLabel}>نشط</Paragraph>
            </View>
            <View style={styles.statItem}>
              <Paragraph style={[styles.statNumber, { color: '#F44336' }]}>
                {bannedUsers.length}
              </Paragraph>
              <Paragraph style={styles.statLabel}>محظور</Paragraph>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* شريط البحث */}
      <Card style={styles.card}>
        <Card.Content>
          <Searchbar
            placeholder="البحث عن مستخدم..."
            onChangeText={setSearchQuery}
            value={searchQuery}
            style={styles.searchbar}
          />
        </Card.Content>
      </Card>

      {/* قائمة المستخدمين */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>قائمة المستخدمين ({filteredUsers.length})</Title>
          
          {filteredUsers.length === 0 ? (
            <View style={styles.emptyState}>
              <Paragraph style={styles.emptyText}>
                {searchQuery ? 'لا توجد نتائج للبحث' : 'لا يوجد مستخدمون بعد'}
              </Paragraph>
            </View>
          ) : (
            filteredUsers.map((user, index) => (
              <View key={user.user_id}>
                <List.Item
                  title={`${user.first_name || ''} ${user.last_name || ''}`.trim() || 'بدون اسم'}
                  description={`@${user.username || 'بدون معرف'} • ${user.user_id} • انضم: ${formatDate(user.join_date)}`}
                  left={(props) => (
                    <Avatar.Text
                      {...props}
                      size={40}
                      label={getInitials(user.first_name, user.last_name)}
                      style={{
                        backgroundColor: user.is_banned ? '#F44336' : '#2196F3'
                      }}
                    />
                  )}
                  right={(props) => (
                    <View style={styles.userActions}>
                      <Chip
                        icon={user.is_banned ? 'block-helper' : 'check-circle'}
                        style={[
                          styles.statusChip,
                          {
                            backgroundColor: user.is_banned ? '#F44336' : '#4CAF50'
                          }
                        ]}
                        textStyle={{ color: 'white', fontSize: 10 }}
                      >
                        {user.is_banned ? 'محظور' : 'نشط'}
                      </Chip>
                      
                      {user.is_banned ? (
                        <Button
                          mode="outlined"
                          onPress={() => handleUnbanUser(user.user_id, user.username)}
                          icon="account-check"
                          compact
                          style={styles.actionButton}
                        >
                          إلغاء الحظر
                        </Button>
                      ) : (
                        <Button
                          mode="outlined"
                          onPress={() => handleBanUser(user.user_id, user.username)}
                          icon="block-helper"
                          textColor="#F44336"
                          compact
                          style={styles.actionButton}
                        >
                          حظر
                        </Button>
                      )}
                    </View>
                  )}
                  style={[
                    styles.userItem,
                    { opacity: user.is_banned ? 0.7 : 1 }
                  ]}
                />
                {index < filteredUsers.length - 1 && <Divider />}
              </View>
            ))
          )}
        </Card.Content>
      </Card>

      {/* إجراءات سريعة */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>إجراءات سريعة</Title>
          
          <View style={styles.quickActions}>
            <Button
              mode="outlined"
              onPress={() => Alert.alert('قريباً', 'سيتم إضافة هذه الميزة قريباً')}
              icon="export"
              style={styles.quickActionButton}
            >
              تصدير القائمة
            </Button>
            
            <Button
              mode="outlined"
              onPress={() => Alert.alert('قريباً', 'سيتم إضافة هذه الميزة قريباً')}
              icon="message-bulleted"
              style={styles.quickActionButton}
            >
              رسالة جماعية
            </Button>
          </View>
        </Card.Content>
      </Card>

      {/* نصائح الإدارة */}
      <Card style={styles.card}>
        <Card.Content>
          <Title>نصائح الإدارة</Title>
          <List.Item
            title="مراقبة النشاط"
            description="راقب نشاط المستخدمين بانتظام للكشف عن أي سلوك مشبوه"
            left={(props) => <List.Icon {...props} icon="eye" />}
          />
          <Divider />
          <List.Item
            title="التواصل الفعال"
            description="تواصل مع المستخدمين بشكل مهذب ومهني"
            left={(props) => <List.Icon {...props} icon="message-text" />}
          />
          <Divider />
          <List.Item
            title="النسخ الاحتياطية"
            description="احتفظ بنسخ احتياطية من بيانات المستخدمين"
            left={(props) => <List.Icon {...props} icon="backup-restore" />}
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
  statsCard: {
    marginBottom: 16,
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
    marginBottom: 16,
    elevation: 4,
  },
  searchbar: {
    elevation: 0,
    backgroundColor: '#f5f5f5',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyText: {
    color: '#666',
    textAlign: 'center',
  },
  userItem: {
    paddingVertical: 8,
  },
  userActions: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  statusChip: {
    marginBottom: 8,
  },
  actionButton: {
    minWidth: 100,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  quickActionButton: {
    flex: 1,
    marginHorizontal: 8,
  },
});