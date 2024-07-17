// src/utils/auth.js

export const setToken = (token) => {
    localStorage.setItem('jwtToken', token);
  };
  
  export const getToken = () => {
    return localStorage.getItem('jwtToken');
  };
  
  export const removeToken = () => {
    localStorage.removeItem('jwtToken');
  };
  