//? Import Axios
import axios from 'axios';                                                                      //* Import Axios for making HTTP requests

//? Base config for Axios
const API_BASE_URL = 'http://127.0.0.1:8000';                                                   //* Base URL for the API

//? Create an Axios instance with the base URL
const api = axios.create({
    baseURL: API_BASE_URL,                                                                      //* Set the base URL for all requests
    headers: {
        'Content-Type': 'application/json',                                                     //* Set the content type for requests
    },
})

//? Global error handler for Axios
api.interceptors.response.use(
    (response) => response,                                                                     //* If the response is successful, return it
    (error) => {
        console.error('API error:', error.response?.data || error.message);                     //* Log the error for debugging
        return Promise.reject(error);                                                           //* Reject the promise with the error
    }
);


//? <|------------------Home Page APIs------------------|>



//? <|------------------Services APIs-------------------|>



//? <|-------------------About Us APIs------------------|>



//? <|-------------------Contact APIs-------------------|>



//? <|-------------------Orders APIs--------------------|>



//? <|--------------------Cart APIs---------------------|>
