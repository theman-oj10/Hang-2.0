import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, Image, StyleSheet, ActivityIndicator } from 'react-native';

const GroupsScreen = ({ navigation }) => {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGroups();
  }, []);

  const fetchGroups = async () => {
    try {
      const response = await fetch('http://127.0.0.1:4000/api/get_group'); // Fetch data from your backend API
      const data = await response.json();
      setGroups([
        {
          id: '1',
          name: 'Uni Friends',
          members: data,
        },
        {
          id: '2',
          name: 'Family',
          members: data,
        },
        {
          id: '3',
          name: 'Work Buddies',
          members: data,
        },
      ]);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching groups:', error);
      setLoading(false);
    }
  };

  // Function to get avatar based on the username
  const getAvatarForUser = (userName) => {
    const avatarMap = {
      'johndoe123': require('../assets/johndoe.png'),
      'emilyc987': require('../assets/person2.png'),
      'alex_mart': require('../assets/person3.png'),
      'sophieleee': require('../assets/person4.png'),
      'default': require('../assets/splash.png'), // Fallback image
    };

    return avatarMap[userName] || avatarMap['default']; // Return default image if username not found
  };

  const renderItem = ({ item }) => (
    <TouchableOpacity 
      style={styles.groupItem} 
      onPress={() => navigation.navigate('ItineraryList', { groupName: item.name })}
    >
      <View style={styles.groupHeader}>
        <Text style={styles.groupName}>{item.name}</Text>
        <View style={styles.avatarGroup}>
          {item.members.map((member, index) => (
            <TouchableOpacity
              key={index}
              onPress={() => navigation.navigate('Profile', { profile: member, profileImage: getAvatarForUser(member.userName) })} // Pass profile and profileImage
            >
              <Image
                source={getAvatarForUser(member.userName)} // Get image based on username
                style={[
                  styles.avatar,
                  { zIndex: item.members.length - index } // To maintain proper stacking order
                ]}
              />
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={groups}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#E6F7FF',
    padding: 16,
  },
  listContent: {
    paddingVertical: 16,
  },
  groupItem: {
    backgroundColor: '#ffffff',
    padding: 20,
    borderRadius: 10,
    marginBottom: 20,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
  },
  groupHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  groupName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  avatarGroup: {
    flexDirection: 'row',
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    marginLeft: -8, // Overlap avatars slightly
    borderWidth: 2,
    borderColor: '#fff',
  },
});

export default GroupsScreen;
