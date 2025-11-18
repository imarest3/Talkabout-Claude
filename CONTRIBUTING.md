# Guía de Contribución

Gracias por tu interés en contribuir a Talkabout. Este documento proporciona pautas para contribuir al proyecto.

## Código de Conducta

- Sé respetuoso y profesional
- Acepta críticas constructivas
- Enfócate en lo mejor para la comunidad
- Muestra empatía hacia otros miembros

## Cómo Contribuir

### Reportar Bugs

1. Verifica que el bug no haya sido reportado antes
2. Abre un issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots si aplica
   - Versión de la aplicación
   - Sistema operativo

### Sugerir Mejoras

1. Abre un issue describiendo:
   - La funcionalidad propuesta
   - Por qué sería útil
   - Ejemplos de uso
   - Posible implementación

### Pull Requests

1. **Fork el repositorio**

2. **Crea una rama**
   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```

3. **Haz tus cambios**
   - Sigue el estilo de código existente
   - Añade tests si es aplicable
   - Actualiza documentación

4. **Commit**
   ```bash
   git commit -m "Descripción clara del cambio"
   ```

5. **Push**
   ```bash
   git push origin feature/mi-nueva-funcionalidad
   ```

6. **Abre Pull Request**
   - Describe los cambios
   - Referencia issues relacionados
   - Incluye screenshots si aplica

## Estándares de Código

### Python/Django
- Seguir PEP 8
- Usar type hints cuando sea posible
- Documentar funciones y clases
- Mantener líneas < 100 caracteres

### Git Commits
- Usar mensajes descriptivos
- Presente imperativo: "Add feature" no "Added feature"
- Primera línea < 50 caracteres
- Cuerpo del mensaje si es necesario

### Tests
- Escribir tests para nuevas funcionalidades
- Mantener cobertura > 80%
- Tests deben ser independientes

## Proceso de Review

1. Un maintainer revisará tu PR
2. Puede solicitar cambios
3. Una vez aprobado, se hará merge
4. Tu contribución será acreditada

## Preguntas

Si tienes preguntas, abre un issue con la etiqueta "question".

¡Gracias por contribuir!
