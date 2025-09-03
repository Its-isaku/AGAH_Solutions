//? Imports
import React, { createContext, useContext, useState, useEffect } from 'react';

//? Create Cart Context
const CartContext = createContext();

//? Cart Provider Component
export const CartProvider = ({ children }) => {
    //? State Variables
    const [cartItems, setCartItems] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isInitialized, setIsInitialized] = useState(false);

    //* Load cart from localStorage on mount
    useEffect(() => {
        const savedCart = localStorage.getItem('agah_cart');
        if (savedCart) {
            try {
                setCartItems(JSON.parse(savedCart));
            } catch (err) {
                console.error('Error loading cart from storage:', err);
            }
        }
        setIsInitialized(true);
    }, []);

    //* Save cart to localStorage whenever it changes (but not on initial load)
    useEffect(() => {
        if (isInitialized) {
            localStorage.setItem('agah_cart', JSON.stringify(cartItems));
        }
    }, [cartItems, isInitialized]);

    //? Functions
    //* Add item to cart
    const addToCart = (item) => {
        setCartItems(prevItems => {
            //* Check if item with same service and dimensions exists
            const existingItemIndex = prevItems.findIndex(
                cartItem => 
                    cartItem.service === item.service &&
                    cartItem.length_dimensions === item.length_dimensions &&
                    cartItem.width_dimensions === item.width_dimensions &&
                    cartItem.height_dimensions === item.height_dimensions
            );

            if (existingItemIndex > -1) {
                //* Update quantity if item exists
                const updatedItems = [...prevItems];
                updatedItems[existingItemIndex].quantity += item.quantity;
                return updatedItems;
            } else {
                //* Add new item with unique ID
                return [...prevItems, {
                    ...item,
                    cartItemId: Date.now() + Math.random(), //* Unique ID for cart management
                }];
            }
        });
    };

    //* Remove item from cart
    const removeFromCart = (cartItemId) => {
        setCartItems(prevItems => 
            prevItems.filter(item => item.cartItemId !== cartItemId)
        );
    };

    //* Update item quantity
    const updateQuantity = (cartItemId, newQuantity) => {
        if (newQuantity <= 0) {
            removeFromCart(cartItemId);
            return;
        }

        setCartItems(prevItems =>
            prevItems.map(item =>
                item.cartItemId === cartItemId
                    ? { ...item, quantity: newQuantity }
                    : item
            )
        );
    };

    //* Clear entire cart
    const clearCart = () => {
        setCartItems([]);
        localStorage.removeItem('agah_cart');
    };

    //* Calculate total estimated price
    const calculateTotal = () => {
        return cartItems.reduce((total, item) => {
            //* Use estimated price if available, otherwise use base price
            const price = item.estimated_unit_price || item.base_price || 0;
            return total + (price * item.quantity);
        }, 0);
    };

    //* Get cart item count
    const getCartItemCount = () => {
        return cartItems.reduce((count, item) => count + item.quantity, 0);
    };

    //? Context value
    const value = {
        cartItems,
        isLoading,
        error,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        calculateTotal,
        getCartItemCount,
    };

    return (
        <CartContext.Provider value={value}>
            {children}
        </CartContext.Provider>
    );
};

//? Custom hook to use Cart Context
export const useCart = () => {
    const context = useContext(CartContext);
    if (!context) {
        throw new Error('useCart must be used within a CartProvider');
    }
    return context;
};

export default CartContext;