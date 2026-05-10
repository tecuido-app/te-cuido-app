# Demo TE CUIDO — script del pitch (3 minutos)

## Pre-flight (5 min antes del pitch)

- [ ] Agente corriendo en :8000 → en WSL: `uvicorn agent.api:app --port 8000`
- [ ] Dashboard corriendo en :3000 → en PowerShell: `npm start` (en carpeta dashboard/)
- [ ] Browser abierto en `http://localhost:3000`
- [ ] Tab con [Solana Explorer devnet](https://explorer.solana.com/?cluster=devnet)
- [ ] Telegram en el celular de alguien del equipo (si está configurado)
- [ ] Comando `curl` listo en clipboard (ver abajo)
- [ ] Video pre-grabado de 60s abierto en otra tab (plan B)

## Script

### 0:00–0:20 — El problema

> *"Carmen tiene 78 años. Su hija Juliana trabaja y vive con la culpa de no poder estar siempre. El dispositivo Ato se agota cada vez que sale. La gente paga por estos sistemas — pero no existen acá."*

### 0:20–1:00 — Sistema activo

> Mostrar el dashboard en verde.
> *"Esto es lo que ve Juliana. Carmen está bien. El sistema monitorea signos vitales en tiempo real."*

> Señalar los números que cambian cada 5 segundos.
> *"Los datos se actualizan solos — no hay nada que hacer, solo mirar."*

### 1:00–2:10 — La emergencia

> *"Pero hoy a las 14:32, el sistema detecta frecuencia cardíaca crítica."*

> **En la terminal del agente (WSL), pegar este comando:**
> ```bash
> curl -X POST "http://localhost:8000/api/simulate?event_type=low_hr"
> ```

> En la terminal del agente aparece:
> - `[AIFilter]` evaluando con Gemini — "frecuencia cardíaca peligrosamente baja"
> - `[Solana]` transaction hash: `5tNh...`
> - Estado pasa a `alert`

> **En el dashboard**, usar el botón DevMode (esquina inferior derecha) para mostrar estado ALERT.
> *"Primer paso: 60 segundos de gracia para que Carmen confirme que está bien."*

> Si el contador llega a cero o se fuerza con DevMode → estado EMERGENCY.
> *"Sin respuesta. El agente notifica a Juliana por Telegram."*

> Si Telegram está configurado → mostrar el celular vibrando.

> *"Y todo esto queda firmado en Solana."*
> Abrir el tab del Explorer y mostrar las transacciones.

### 2:10–2:40 — Cierre

> *"Esto no es una alarma. Es un agente que actúa, decide y deja prueba forense. Hoy."*

> Pausa de 2 segundos.

> *"Te Cuido. Sistema preventivo inteligente para cuidar a quienes más importan."*

---

## Comandos rápidos

```bash
# Simular frecuencia cardíaca baja (bradicardia)
curl -X POST "http://localhost:8000/api/simulate?event_type=low_hr"

# Simular caída
curl -X POST "http://localhost:8000/api/simulate?event_type=fall"

# Simular SpO2 bajo (hipoxia)
curl -X POST "http://localhost:8000/api/simulate?event_type=low_spo2"

# Confirmar "Carmen está bien" (cancela la escalada activa)
curl -X POST http://localhost:8000/api/wellbeing

# Ver estado actual del agente
curl http://localhost:8000/api/status
```

---

## Plan B — si la devnet de Solana se cae

- Usar `USE_MOCK_SOLANA=true` en `.env` — el agente sigue funcionando igual pero no escribe on-chain
- El dashboard funciona igual (datos mockeados)
- Las TXes del Explorer: abrir las URLs reales antes del pitch y tenerlas en tabs

## Plan C — si el agente no arranca

- Usar solo el dashboard con DevMode para mostrar el flujo UX completo
- El DevMode (botón esquina inferior derecha) cicla ok → alert → emergency
- Los números de vitales se actualizan solos desde `/api/vitals` local
