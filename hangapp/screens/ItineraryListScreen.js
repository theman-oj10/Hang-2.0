import React, { useState, useEffect } from 'react';
import { View, Text, Image, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import BottomNavBar from './BottomNavBar'; // Import the BottomNavBar component

const sampleAvatars = [
  { id: 1, source: require('../assets/logo.png') },
  { id: 2, source: require('../assets/logo.png') },
  { id: 3, source: require('../assets/logo.png') },
  { id: 4, source: require('../assets/logo.png') },
  { id: 5, source: require('../assets/logo.png') },
];

const ItineraryListScreen = ({ navigation, route }) => {
  const [itineraries, setItineraries] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch data when the component is mounted
  useEffect(() => {
    fetchItineraries();
  }, []);

  const fetchItineraries = async () => {
    try {
      // Replace with your actual API URL
      const response = await fetch('');
      const data = await response.json();

      // Map the data to match your itinerary structure, including the price
      const mappedData = data.map((restaurant, index) => ({
        id: index + 1,
        title: `Itinerary Option ${index + 1}`,
        activities: [
          {
            time: "09:00 AM",
            activity: `Visit ${restaurant.name}`,
            description: `Enjoy a meal at ${restaurant.name}, rated ${restaurant.rating} stars. Price: ${restaurant.price}. Located at ${restaurant.address}.`,
          }
        ],
        image: require('../assets/logo.png'), // Placeholder image, replace as needed
      }));

      setItineraries(mappedData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching itineraries:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.groupTitle}>{route.params.groupName}</Text>
      <FlatList
        data={itineraries}
        renderItem={({ item }) => (
          <TouchableOpacity 
            style={styles.card} 
            onPress={() => navigation.navigate('ItineraryDetail', { itinerary: item })}
          >
            <Image source={item.image} style={styles.cardImage} />
            <View style={styles.cardContent}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{item.title}</Text>
                <View style={styles.avatarGroup}>
                  {sampleAvatars.map((avatar) => (
                    <Image key={avatar.id} source={avatar.source} style={styles.avatar} />
                  ))}
                </View>
              </View>
            </View>
          </TouchableOpacity>
        )}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />
      <BottomNavBar />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#E6F7FF',
    padding: 16,
  },
  groupTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  listContent: {
    paddingBottom: 32,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    marginBottom: 20,
    overflow: 'hidden',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
  },
  cardImage: {
    width: '100%',
    height: 160,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  cardContent: {
    padding: 16,
    backgroundColor: '#FFF',
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 20,
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
    marginLeft: -8,
    borderWidth: 2,
    borderColor: '#fff',
  },
});

export default ItineraryListScreen;
