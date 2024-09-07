import React from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import Ionicons from 'react-native-vector-icons/Ionicons';

const BottomNavBar = () => {
  const navigation = useNavigation();

  return (
    <View style={styles.navContainer}>
      <TouchableOpacity onPress={() => navigation.navigate('Groups')} style={styles.navButton}>
        <Ionicons name="list-outline" size={28} color="#004AAD" />
        <Text style={styles.navText}>Groups</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => navigation.navigate('Chat')} style={styles.navButton}>
        <Ionicons name="chatbox-outline" size={28} color="#004AAD" />
        <Text style={styles.navText}>Chat</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => navigation.navigate('Hang')} style={styles.navButton}>
        <Ionicons name="people-outline" size={28} color="#004AAD" />
        <Text style={styles.navText}>Hang</Text>
      </TouchableOpacity>
      <TouchableOpacity onPress={() => navigation.navigate('Profile')} style={styles.navButton}>
        <Ionicons name="person-outline" size={28} color="#004AAD" />
        <Text style={styles.navText}>Profile</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  navContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 10,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#ccc',
  },
  navButton: {
    alignItems: 'center',
  },
  navText: {
    fontSize: 12,
    color: '#004AAD',
  },
});

export default BottomNavBar;
