import React from 'react';
import { View, Text, ScrollView, Image, StyleSheet, SafeAreaView } from 'react-native';
import BottomNavBar from './BottomNavBar';

const ItineraryDetailScreen = ({ route }) => {
  const { itinerary } = route.params;

  const renderActivity = (item, type) => (
    <View style={styles.activityItem}>
      <Text style={styles.type}>{type}</Text>
      <Text style={styles.time}>{item.time}</Text>
      <Text style={styles.activity}>{item.activity}</Text>
      {item.image && (
        <Image source={{ uri: item.image }} style={styles.activityImage} />
      )}
      <Text style={styles.description}>{item.description}</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>{itinerary.title}</Text>
        {renderActivity(itinerary.restaurant, 'Restaurant')}
        {renderActivity(itinerary.activity, 'Activity')}
      </ScrollView>
      <BottomNavBar />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#E6F7FF',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginVertical: 20,
    marginHorizontal: 16,
    color: '#004AAD',
  },
  activityItem: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginHorizontal: 16,
    marginBottom: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 1,
  },
  type: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#004AAD',
    marginBottom: 8,
  },
  time: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  activity: {
    fontSize: 16,
    color: '#004AAD',
    marginBottom: 8,
  },
  activityImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: '#666',
  },
});

export default ItineraryDetailScreen;