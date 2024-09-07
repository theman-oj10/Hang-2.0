import React from 'react';
import { View, Text, FlatList, TouchableOpacity, Image, StyleSheet } from 'react-native';

const sampleAvatars = [
  { id: 1, source: require('../assets/logo.png') },
  { id: 2, source: require('../assets/logo.png') },
  { id: 3, source: require('../assets/logo.png') },
  { id: 4, source: require('../assets/logo.png') },
  { id: 5, source: require('../assets/logo.png') },
];

// Function to get a random subset of avatars
const getRandomAvatars = (avatars) => {
  const randomCount = Math.floor(Math.random() * avatars.length) + 1; // Random count between 1 and the length of avatars
  const shuffled = avatars.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, randomCount);
};

const groups = [
  {
    id: '1',
    name: 'Family Vacation',
    avatars: getRandomAvatars(sampleAvatars),
  },
  {
    id: '2',
    name: 'Friends Reunion',
    avatars: getRandomAvatars(sampleAvatars),
  },
  {
    id: '3',
    name: 'Work Retreat',
    avatars: getRandomAvatars(sampleAvatars),
  },
];

const GroupsScreen = ({ navigation }) => {
  const renderItem = ({ item }) => (
    <TouchableOpacity 
      style={styles.groupItem} 
      onPress={() => navigation.navigate('ItineraryList', { groupName: item.name })}
    >
      <View style={styles.groupHeader}>
        <Text style={styles.groupName}>{item.name}</Text>
        <View style={styles.avatarGroup}>
          {item.avatars.map((avatar, index) => (
            <Image key={index} source={avatar.source} style={styles.avatar} />
          ))}
        </View>
      </View>
    </TouchableOpacity>
  );

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
