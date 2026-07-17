# ADR-0001: Aplicacion local como version activa

- Fecha: 2026-04-21
- Estado: Aceptada

## Contexto

El proyecto nacio como notebook de Google Colab y luego tuvo una version en
Hugging Face Spaces. La operacion cotidiana requiere una herramienta personal,
estable y ejecutable en Windows, sin depender de un servicio externo.

## Decision

Mantener una unica version activa como aplicacion local con interfaz HTML. El
notebook queda en `notebooks/` solo como antecedente y Hugging Face deja de ser
un destino de despliegue.

## Consecuencias

- La aplicacion se ejecuta en `http://127.0.0.1:7861`.
- La disponibilidad depende del equipo local, no de un servicio remoto.
- La instalacion y el empaquetado para Windows pasan a formar parte del
  mantenimiento del proyecto.
- El README debe describir solo el flujo local activo.
