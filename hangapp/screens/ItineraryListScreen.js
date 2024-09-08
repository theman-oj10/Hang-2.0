import React, { useState, useEffect, useLayoutEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, Image, ActivityIndicator, StyleSheet, SafeAreaView } from 'react-native';
import BottomNavBar from './BottomNavBar'; 

const ItineraryListScreen = ({ navigation, route }) => {
  const [itineraries, setItineraries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchItineraries();
  }, []);

  useLayoutEffect(() => {
    navigation.setOptions({
      headerShown: false, // This hides the default header
    });
  }, [navigation]);

  const fetchItineraries = async () => {
    try {
      const response = await fetch('http://127.0.0.1:4000//api/recommend2');
      const data = await response.json();

      if (data.status === 'success') {
        const mappedData = [];
        for (let i = 0; i < 3; i++) {
          const restaurant = data.restaurant_recommendations[i];
          const activity = data.activity_recommendations[i];

          if (restaurant && activity) {
            mappedData.push({
              id: i + 1,
              title: `Itinerary ${i + 1}`,
              restaurant: {
                time: '12:00 PM',
                activity: `Dine at ${restaurant.name}`,
                description: restaurant.explanation,
                image: restaurant.image_url || null,
                price: restaurant.price, 
                rating: restaurant.rating, 
              },
              activity: {
                time: '3:00 PM',
                activity: `Visit ${activity.name}`,
                description: activity.explanation,
                image: activity.image_url || null,
                price: activity.price,  
                rating: activity.rating,
              },
            });
          }
        }

        setItineraries(mappedData);
      } else {
        console.error('API response was not successful');
      }
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
    <SafeAreaView style={styles.container}>
      <Text style={styles.groupTitle}>{route.params?.groupName || 'Family Vacation'}</Text>
      <FlatList
        data={itineraries}
        renderItem={({ item }) => (
          <TouchableOpacity 
            style={styles.card} 
            onPress={() => navigation.navigate('ItineraryDetail', { itinerary: item })} 
          >
            <Image 
              source={{ uri: item.restaurant.image || item.activity.image || 'https://via.placeholder.com/300' }} 
              style={styles.cardImage} 
            />
            <View style={styles.cardContent}>
              <Text style={styles.cardTitle}>{item.title}</Text>
              <Text style={styles.cardDescription} numberOfLines={2}>
                {item.restaurant.activity}, {item.activity.activity}
              </Text>
            </View>
          </TouchableOpacity>
        )}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={true}
      />
      <BottomNavBar />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  groupTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    padding: 16,
    textAlign: 'center',
    color: '#004AAD',
  },
  listContent: {
    padding: 16,
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 8,
    overflow: 'hidden',
    marginBottom: 16,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  cardImage: {
    width: '100%',
    height: 200,
    resizeMode: 'cover',
  },
  cardContent: {
    padding: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
    color: '#004AAD',
  },
  cardDescription: {
    fontSize: 14,
    color: '#666',
  },
});

export default ItineraryListScreen;
