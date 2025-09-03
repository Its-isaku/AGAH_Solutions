# Sistema de Notificaciones Personalizado

## 📋 Descripción
Sistema de notificaciones personalizado creado para AGAH Solutions que reemplaza a @mosespace/toast con un diseño consistente con la aplicación.

## 🚀 Características
- **Estilos personalizados** que coinciden con el diseño de la aplicación
- **Múltiples tipos** de notificación (success, error, warning, info, loading)
- **Notificaciones de promesa** para operaciones asíncronas
- **Animaciones suaves** con efectos de entrada y salida
- **Z-index alto** (9999) para aparecer sobre todo el contenido
- **Responsive** y optimizado para móviles
- **Auto-eliminación** configurable

## 📁 Archivos Creados
- `src/components/common/Toast.jsx` - Componente principal y hook
- `src/context/ToastContext.jsx` - Context provider
- `src/style/Toast.css` - Estilos personalizados

## 🔧 Uso Básico

### 1. Importar el hook en tu componente
```jsx
import { useToastContext } from '../context/ToastContext';
```

### 2. Usar las notificaciones
```jsx
function MiComponente() {
    const { success, error, warning, info, promise } = useToastContext();

    const handleClick = () => {
        success('¡Operación exitosa!');
        error('Algo salió mal');
        warning('Advertencia importante');
        info('Información útil');
    };

    return (
        <button onClick={handleClick}>
            Mostrar notificación
        </button>
    );
}
```

## 🎯 Tipos de Notificaciones

### Success Toast
```jsx
success('¡Mensaje enviado exitosamente!');
success('Operación completada', 5000); // 5 segundos de duración
```

### Error Toast
```jsx
error('Error al procesar la solicitud');
error('Error crítico', 0); // No se auto-elimina
```

### Warning Toast
```jsx
warning('Verifica los datos antes de continuar');
```

### Info Toast
```jsx
info('Nueva actualización disponible');
```

### Promise Toast (Para operaciones asíncronas)
```jsx
// Ejemplo básico
promise(
    fetch('/api/data'),
    {
        loading: 'Cargando datos...',
        success: 'Datos cargados exitosamente',
        error: 'Error al cargar datos'
    }
);

// Ejemplo con función async
const enviarFormulario = async () => {
    try {
        await promise(
            api.contact.sendForm(formData),
            {
                loading: 'Enviando formulario...',
                success: '¡Formulario enviado con éxito!',
                error: 'Error al enviar formulario'
            }
        );
        
        // El formulario se envió correctamente
        resetForm();
    } catch (error) {
        // Manejar error adicional si es necesario
        console.error('Error:', error);
    }
};
```

## 🎨 Personalización de Estilos

Los estilos están definidos en `src/style/Toast.css` y siguen la paleta de colores de la aplicación:

- **Success**: Verde (#10B981)
- **Error**: Rojo (#EF4444)  
- **Warning**: Amarillo (#F59E0B)
- **Info**: Azul (#3B82F6)
- **Loading**: Azul corporativo (#78B7D0)

### Colores principales usados:
- Fondo: `rgba(255, 255, 255, 0.1)` con `backdrop-filter: blur(15px)`
- Texto: `#F4E7E1`
- Borde: `rgba(120, 183, 208, 0.2)`

## 📱 Responsive
- **Desktop**: Esquina superior derecha con ancho máximo de 400px
- **Mobile**: Se adapta al ancho de la pantalla con márgenes reducidos

## ⚡ Configuración Avanzada

### Duración personalizada
```jsx
success('Mensaje temporal', 2000); // 2 segundos
warning('Mensaje persistente', 0); // No se auto-elimina
```

### Eliminación manual
```jsx
const { success, removeToast } = useToastContext();

const toastId = success('Mensaje con control manual', 0);

// Eliminar después de una acción específica
setTimeout(() => {
    removeToast(toastId);
}, 5000);
```

## 🔄 Migración desde @mosespace/toast

### Antes:
```jsx
import { toast } from '@mosespace/toast';

toast.success('Mensaje de éxito');
toast.error('Mensaje de error');
```

### Después:
```jsx
import { useToastContext } from '../context/ToastContext';

const { success, error } = useToastContext();

success('Mensaje de éxito');
error('Mensaje de error');
```

## 🛠️ Integración Completa

El sistema ya está integrado en:
1. ✅ `main.jsx` - ToastProvider envuelve toda la aplicación
2. ✅ `Contact.jsx` - Ejemplo de uso con formulario y botones de prueba
3. ✅ Estilos personalizados que coinciden con el diseño

## 🎮 Botones de Prueba
En la página de contacto hay botones de demostración para probar todos los tipos de toast:
- **Success Toast** - Verde
- **Error Toast** - Rojo  
- **Warning Toast** - Amarillo
- **Promise Toast** - Azul (simula operación de 3 segundos)

## 📝 Notas Importantes
- El sistema tiene un **z-index de 9999** para aparecer sobre todo el contenido
- Las notificaciones se posicionan en la **esquina superior derecha**
- Son **clickeables** para cerrar manualmente
- Incluyen **animaciones suaves** de entrada y salida
- El diseño es **consistente** con las cartas y modales de la aplicación
