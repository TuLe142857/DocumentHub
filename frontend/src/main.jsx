import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from './store/store.jsx';
import './index.css';
import App from './App.jsx';
import ModalProvider from '@/modal/ModalProvider.jsx';
createRoot(document.getElementById('root')).render(
  // <StrictMode>
    <ModalProvider>
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    </ModalProvider>
  // </StrictMode>
);
