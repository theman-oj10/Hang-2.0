import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import BottomNavBar from './BottomNavBar'; // Import the BottomNavBar component

const ItineraryDetailScreen = ({ route }) => {
  const { itinerary } = route.params;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{itinerary.title}</Text>
      <FlatList
        data={itinerary.activities}
        renderItem={({ item }) => (
          <View style={styles.activityItem}>
            <Text style={styles.time}>{item.time}</Text>
            <Text style={styles.activity}>{item.activity}</Text>
            <Text style={styles.description}>{item.description}</Text>
          </View>
        )}
        keyExtractor={(item, index) => index.toString()}
      />
      <BottomNavBar />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#E6F7FF',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#004AAD',
  },
  activityItem: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#ccc',
    marginBottom: 10,
  },
  time: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  activity: {
    fontSize: 16,
    color: '#004AAD',
  },
  description: {
    fontSize: 14,
    color: '#777',
  },
});

export default ItineraryDetailScreen;
