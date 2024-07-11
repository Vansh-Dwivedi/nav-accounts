import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Navigate } from 'react-router-dom';
import './App.css';
import moment from 'moment-timezone';
import { isLoggedIn } from 'login/auth/AuthWrapper';


function App() {
  const [users, setUsers] = useState([]);
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [profilePic, setProfilePic] = useState(null);
  const [descriptionFile, setDescriptionFile] = useState(null);
  const [editUserId, setEditUserId] = useState(null);
  const [error, setError] = useState({ name: '', address: '', phoneNumber: '', profilePic: '', descriptionFile: '' });
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    if (isLoggedIn) {
      fetchUsers();
    }
  }, [isLoggedIn]);

  const fetchUsers = async () => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://127.0.0.1:5000/users', {
        headers: {
          'x-access-tokens': token,
        },
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      console.log('Fetched users:', data);
      setUsers(data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleNameChange = (e) => {
    const value = e.target.value;
    setName(value);
    setError((prev) => ({ ...prev, name: '' }));
  };

  const handleAddressChange = (e) => {
    const value = e.target.value;
    setAddress(value);
    setError((prev) => ({ ...prev, address: '' }));
  };

  const handlePhoneNumberChange = (e) => {
    const value = e.target.value;
    setPhoneNumber(value);
    setError((prev) => ({ ...prev, phoneNumber: '' }));
  };

  const handleProfilePicChange = (e) => {
    setProfilePic(e.target.files[0]);
  };

  const handleDescriptionFileChange = (e) => {
    setDescriptionFile(e.target.files[0]);
  };

  const addUser = async () => {
    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('name', name);
    formData.append('address', address);
    formData.append('phone_number', phoneNumber);
    formData.append('profile_pic', profilePic);
    formData.append('description_file', descriptionFile);

    try {
      const response = await fetch('http://127.0.0.1:5000/user', {
        method: 'POST',
        headers: {
          'x-access-tokens': token,
        },
        body: formData,
      });
      if (response.ok) {
        fetchUsers();
        setName('');
        setAddress('');
        setPhoneNumber('');
        setProfilePic(null);
        setDescriptionFile(null);
      } else {
        console.error('Failed to add user');
      }
    } catch (error) {
      console.error('Error adding user:', error);
    }
  };

  const updateUser = async (id) => {
    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('name', name);
    formData.append('address', address);
    formData.append('phone_number', phoneNumber);
    formData.append('profile_pic', profilePic);
    formData.append('description_file', descriptionFile);

    try {
      const response = await fetch(`http://127.0.0.1:5000/user/${id}`, {
        method: 'PUT',
        headers: {
          'x-access-tokens': token,
        },
        body: formData,
      });
      if (response.ok) {
        fetchUsers();
        setName('');
        setAddress('');
        setPhoneNumber('');
        setProfilePic(null);
        setDescriptionFile(null);
        setEditUserId(null);
      } else {
        console.error('Failed to update user');
      }
    } catch (error) {
      console.error('Error updating user:', error);
    }
  };

  const deleteUser = async (id) => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`http://127.0.0.1:5000/user/${id}`, {
        method: 'DELETE',
        headers: {
          'x-access-tokens': token,
        },
      });
      if (response.ok) {
        fetchUsers();
      } else {
        console.error('Failed to delete user');
      }
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  const handleSubmit = () => {
    if (!name || !address || !phoneNumber || !profilePic || !descriptionFile) {
      setError({
        name: !name ? 'Name is required' : '',
        address: !address ? 'Address is required' : '',
        phoneNumber: !phoneNumber ? 'Phone number is required' : '',
        profilePic: !profilePic ? 'Profile picture is required' : '',
        descriptionFile: !descriptionFile ? 'Description file is required' : '',
      });
      return;
    }
    if (editUserId) {
      updateUser(editUserId);
      window.location.reload();
    } else {
      addUser();
      window.location.reload();
    }
  };

  const handleEdit = (user) => {
    setName(user.name);
    setAddress(user.address);
    setPhoneNumber(user.phone_number);
    setEditUserId(user.id);
  };

  const convertToLocalTime = (utcTime) => {
    return moment.utc(utcTime).tz('Asia/Kolkata').format('DD/MM/YYYY, hh:mm:ss A');
  };

  return (
    <Router>
      <div className="App">
        <Route path="/dashboard">
          {isLoggedIn === "authenticated" ?
            <main>
              <div>
                <h2>{editUserId ? 'Edit User' : 'Add User'}</h2>
                <form>
                  <input
                    type="text"
                    placeholder="Name"
                    value={name}
                    onChange={handleNameChange}
                  />
                  {error.name && <div className="error">{error.name}</div>}
                  <input
                    type="text"
                    placeholder="Address"
                    value={address}
                    onChange={handleAddressChange}
                  />
                  {error.address && <div className="error">{error.address}</div>}
                  <input
                    type="text"
                    placeholder="Phone Number"
                    value={phoneNumber}
                    onChange={handlePhoneNumberChange}
                  />
                  {error.phoneNumber && <div className="error">{error.phoneNumber}</div>}
                  <input type="file" onChange={handleProfilePicChange} />
                  {error.profilePic && <div className="error">{error.profilePic}</div>}
                  <input type="file" onChange={handleDescriptionFileChange} />
                  {error.descriptionFile && <div className="error">{error.descriptionFile}</div>}
                  <button type="button" onClick={handleSubmit}>
                    {editUserId ? 'Update User' : 'Add User'}
                  </button>
                </form>
              </div>
              <div className="users-list">
                <h2>Users</h2>
                <ul>
                  {users.length > 0 ? (
                    users.map(user => (
                      <li key={user.id}>
                        <div className='profile-pic'>
                          <img
                            src={`http://localhost:7850/uploads/photos/${user.profile_pic}`}
                            alt={user.name}
                            onError={(e) => {
                            }}
                          />
                          <span>{user.name}</span>
                          <span>{user.address}</span>
                          <span>{user.phone_number}</span>
                          <span>Created At: {convertToLocalTime(user.created_at)}</span>
                        </div>
                        <div className="table-actions">
                          <button className="edit" onClick={() => handleEdit(user)}>Edit</button>
                          <button className="delete" onClick={() => deleteUser(user.id)}>Delete</button>
                          <a
                            href={`http://localhost:7850/uploads/docs/${user.description_file}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            download
                          >
                            Download Description
                          </a>
                        </div>
                      </li>
                    ))
                  ) : (
                    <li>No users found</li>
                  )}
                </ul>
              </div>
            </main>
            : <Navigate to="login/src/index.js" />
          }
        </Route>
      </div>
    </Router>
  );
}

export default App;
