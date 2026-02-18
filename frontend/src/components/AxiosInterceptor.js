
import { useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const AxiosInterceptor = ({ children }) => {
    const navigate = useNavigate();

    useEffect(() => {
        const interceptor = axios.interceptors.response.use(
            (response) => response,
            (error) => {
                if (error.response && (error.response.status === 401 || error.response.status === 403)) {
                    // Si el token es inválido o expiró
                    localStorage.clear();
                    navigate('/login');
                }
                return Promise.reject(error);
            }
        );

        return () => {
            axios.interceptors.response.eject(interceptor);
        };
    }, [navigate]);

    return children;
};

export default AxiosInterceptor;
