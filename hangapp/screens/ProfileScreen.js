import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Image, ScrollView, TextInput, TouchableOpacity, Modal } from 'react-native';
import Ionicons from 'react-native-vector-icons/Ionicons';

const ProfileScreen = ({ route }) => {
  const [profile, setProfile] = useState(route.params?.profile);
  const [profileImage, setProfileImage] = useState(route.params?.profileImage); // Profile image state
  const [isEditing, setIsEditing] = useState(false);
  const [fieldBeingEdited, setFieldBeingEdited] = useState(null);
  const [tempValue, setTempValue] = useState('');

  useEffect(() => {
    if (route.params?.profile) {
      setProfile(route.params.profile);
      setProfileImage(route.params.profileImage); // Set the profile image when the profile changes
    }
  }, [route.params?.profile, route.params?.profileImage]);

  const handleEditPress = (field) => {
    setFieldBeingEdited(field);
    setTempValue(Array.isArray(profile[field]) ? profile[field].join(', ') : profile[field].toString());
    setIsEditing(true);
  };

  const handleSavePress = () => {
    setProfile(prevProfile => ({
      ...prevProfile,
      [fieldBeingEdited]: Array.isArray(prevProfile[fieldBeingEdited]) ? tempValue.split(', ') : tempValue
    }));
    setIsEditing(false);
    setFieldBeingEdited(null);
  };

  if (!profile) {
    return <Text>Loading...</Text>;
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Image
        source={profileImage} // Display profile image passed from GroupsScreen
        style={styles.profileImage}
      />
      <Text style={styles.name}>{profile.name}</Text>
      <Text style={styles.userName}>@{profile.userName}</Text>

      <View style={styles.detailsContainer}>
        <ProfileDetail
          label="Age"
          value={profile.age.toString()}
          onEdit={() => handleEditPress('age')}
        />
        <ProfileDetail
          label="Gender"
          value={profile.gender}
          onEdit={() => handleEditPress('gender')}
        />
        <ProfileDetail
          label="Dietary Preferences"
          value={profile.dietPref.join(', ')}
          onEdit={() => handleEditPress('dietPref')}
        />
        <ProfileDetail
          label="Alcohol"
          value={profile.alcohol ? 'Yes' : 'No'}
          onEdit={() => handleEditPress('alcohol')}
        />
        <ProfileDetail
          label="Favorite Cuisines"
          value={profile.cuisines.join(', ')}
          onEdit={() => handleEditPress('cuisines')}
        />
        <ProfileDetail
          label="Favorite Food"
          value={profile.favFood.join(', ')}
          onEdit={() => handleEditPress('favFood')}
        />
        <ProfileDetail
          label="Special Category"
          value={profile.specialCategory.length > 0 ? profile.specialCategory.join(', ') : 'None'}
          onEdit={() => handleEditPress('specialCategory')}
        />
        <ProfileDetail
          label="Activity Preferences"
          value={profile.activityPref.join(', ')}
          onEdit={() => handleEditPress('activityPref')}
        />
      </View>

      {isEditing && (
        <Modal transparent={true} animationType="slide">
          <View style={styles.modalContainer}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Edit {fieldBeingEdited}</Text>
              <TextInput
                style={styles.modalInput}
                value={tempValue}
                onChangeText={setTempValue}
              />
              <View style={styles.modalButtons}>
                <TouchableOpacity style={styles.saveButton} onPress={handleSavePress}>
                  <Text style={styles.saveButtonText}>Save</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.cancelButton} onPress={() => setIsEditing(false)}>
                  <Text style={styles.cancelButtonText}>Cancel</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>
      )}
    </ScrollView>
  );
};

const ProfileDetail = ({ label, value, onEdit }) => (
  <View style={styles.detailItem}>
    <View style={styles.detailText}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
    <TouchableOpacity onPress={onEdit} style={styles.editButton}>
      <Ionicons name="pencil" size={20} color="#004AAD" />
    </TouchableOpacity>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F0F4F8',
    padding: 20,
  },
  profileImage: {
    width: 150,
    height: 150,
    borderRadius: 75,
    marginBottom: 20,
    borderWidth: 3,
    borderColor: '#004AAD',
  },
  name: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
  },
  userName: {
    fontSize: 18,
    color: '#777',
    marginBottom: 10,
  },
  detailsContainer: {
    width: '100%',
    paddingHorizontal: 20,
  },
  detailItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  detailText: {
    flexDirection: 'column',
  },
  label: {
    fontSize: 16,
    color: '#555',
  },
  value: {
    fontSize: 16,
    color: '#333',
    marginTop: 2,
  },
  editButton: {
    padding: 8,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    width: 300,
    padding: 20,
    backgroundColor: '#FFF',
    borderRadius: 10,
    alignItems: 'center',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#004AAD',
  },
  modalInput: {
    width: '100%',
    padding: 10,
    borderWidth: 1,
    borderColor: '#CCCCCC',
    borderRadius: 8,
    marginBottom: 20,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
  saveButton: {
    flex: 1,
    marginRight: 10,
    backgroundColor: '#004AAD',
    paddingVertical: 10,
    borderRadius: 8,
  },
  saveButtonText: {
    color: '#FFF',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  cancelButton: {
    flex: 1,
    marginLeft: 10,
    backgroundColor: '#CCCCCC',
    paddingVertical: 10,
    borderRadius: 8,
  },
  cancelButtonText: {
    color: '#FFF',
    textAlign: 'center',
    fontWeight: 'bold',
  },
});

export default ProfileScreen;
