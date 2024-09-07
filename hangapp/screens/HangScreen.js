import React from 'react';
import { View, Text, StyleSheet, Button } from 'react-native';

const HangScreen = () => {
  const handleCreateGroup = () => {
    // Implement the group creation logic here
  };

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Create a New Group!</Text>
      <Button title="Create Group" onPress={handleCreateGroup} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#E6F7FF',
    padding: 20,
  },
  text: {
    fontSize: 20,
    marginBottom: 20,
    color: '#333',
  },
});

export default HangScreen;
