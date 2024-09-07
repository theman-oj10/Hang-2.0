import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import LogoScreen from './screens/LogoScreen';
import ItineraryScreen from './screens/ItineraryScreen';
import ItineraryListScreen from './screens/ItineraryListScreen';
import ItineraryDetailScreen from './screens/ItineraryDetailScreen';
import ChatScreen from './screens/ChatScreen';
import HangScreen from './screens/HangScreen';
import ProfileScreen from './screens/ProfileScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Logo">
        <Stack.Screen 
          name="Logo" 
          component={LogoScreen} 
          options={{ headerShown: false }} 
        />
        <Stack.Screen 
          name="Itinerary" 
          component={ItineraryScreen} 
          options={{ headerShown: false }} 
        />
        <Stack.Screen 
          name="ItineraryList" 
          component={ItineraryListScreen} 
          options={{ headerShown: true, title: "Itineraries" }} 
        />
        <Stack.Screen 
          name="ItineraryDetail" 
          component={ItineraryDetailScreen} 
          options={{ headerShown: true, title: "Itinerary Details" }} 
        />
        <Stack.Screen 
          name="Chat" 
          component={ChatScreen} 
          options={{ headerShown: true, title: "Chats" }} 
        />
        <Stack.Screen 
          name="Hang" 
          component={HangScreen} 
          options={{ headerShown: true, title: "Hangouts" }} 
        />
        <Stack.Screen 
          name="Profile" 
          component={ProfileScreen} 
          options={{ headerShown: true, title: "Profile" }} 
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
