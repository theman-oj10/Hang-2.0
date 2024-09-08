import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity } from 'react-native';

const LogoScreen = ({ navigation }) => {
  const handleStartPress = () => {
    navigation.navigate('Itinerary'); // Navigate to the ItineraryScreen
  };

  return (
    <View style={styles.container}>
      <Image
        source={require('../assets/4.png')}
        style={styles.logo}
      />
      <TouchableOpacity style={styles.startButton} onPress={handleStartPress}>
        <Text style={styles.startButtonText}>Let's Get Started!</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#004AAD',
    padding: 20,
  },
  logo: {
    width: '100%', // Make the image take up the full width
    height: '60%', // Adjust the height as needed
    resizeMode: 'contain', // Keep the image's aspect ratio
    marginBottom: 40,
  },
  startButton: {
    backgroundColor: '#ffffff',
    paddingVertical: 15,
    paddingHorizontal: 60,
    borderRadius: 30,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5, // For Android shadow
    flexDirection: 'row',
    alignItems: 'center',
  },
  startButtonText: {
    color: '#004AAD',
    fontSize: 20,
    fontWeight: 'bold',
    letterSpacing: 1,
  },
});

export default LogoScreen;
