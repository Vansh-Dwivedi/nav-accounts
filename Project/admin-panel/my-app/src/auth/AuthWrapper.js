import { createContext, useContext } from "react"
import { RenderHeader } from "../componentss/structure/Header";
import { RenderMenu, RenderRoutes } from "../componentss/structure/RenderNavigation";
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export let isLoggedIn = "unauthenticated";
const AuthContext = createContext();
export const AuthData = () => useContext(AuthContext);


export const AuthWrapper = () => {

     const [usedr, setUsder] = useState('');
     const [pass, setPass] = useState('');

     useEffect(() => {
          fetchUser();
     }, []);

     const fetchUser = async () => {
          try {
               const response = await axios.get('http://localhost:5000/api/users');
               if (response.data.length > 0) {
                    setUsder(response.data[0].username);
                    setPass(response.data[0].password);
               }
          } catch (error) {
               console.error('Error fetching user:', error);
          }
     };

     const [user, setUser] = useState({ name: "", isAuthenticated: false })

     const login = (userName, password) => {

          // Make a call to the authentication API to check the username

          return new Promise((resolve, reject) => {

               if (password === pass && userName === usedr) {
                    setUser({ name: userName, isAuthenticated: true })
                    isLoggedIn = true
                    resolve("success")
               } else if (!password && !userName) {
                    reject("All fields are required!")
               } else {
                    reject("Incorrect username or password!")
               }
          })


     }
     const logout = () => {

          setUser({ ...user, isAuthenticated: false })
     }


     return (

          <AuthContext.Provider value={{ user, login, logout }}>
               <>
                    <RenderHeader />
                    <RenderMenu />
                    <RenderRoutes />
               </>

          </AuthContext.Provider>

     )

}