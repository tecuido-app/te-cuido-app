import type { DashboardData } from './types'

export const mockOk: DashboardData = {
  patientName: 'Carmen García',
  patientAge: 78,
  status: 'ok',
  vitals: {
    heartRate: 72,
    spo2: 97,
    skinTemp: 36.4,
    timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(), // hace 5 minutos
  },
  activeEvent: null,
  history: [
    {
      id: 'evt-001',
      type: 'LowHR',
      severity: 2,
      value: 48,
      timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // hace 2 días
      actions: [
        {
          type: 'GracePeriod',
          timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          txHash: '5tNh8aKpQ2rVxYjLm3nP4cZeA9wBdF6sH1uK7vR8tNh1',
        },
        {
          type: 'WellbeingConfirmed',
          timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000 + 25000).toISOString(),
          txHash: '7xMk9bLpR3sWyZkNm4oQ5dAeB0vCgH7tJ2wL8uS9vMk2',
          note: 'Juliana confirmó bienestar',
        },
        {
          type: 'Resolved',
          timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000 + 26000).toISOString(),
          txHash: '3yPn0cMqS4tXzAlOp5rR6eBfC1wDhI8uK3xM9vT0wPn3',
        },
      ],
      resolved: true,
      resolvedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000 + 26000).toISOString(),
    },
    {
      id: 'evt-002',
      type: 'Fall',
      severity: 3,
      value: 180,
      timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // hace 1 semana
      actions: [
        {
          type: 'GracePeriod',
          timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          txHash: '9aPq1dNrT5uYbBmRs6pS7fCgD2xEiJ9vL4yN0wU1xQr4',
        },
        {
          type: 'NotifiedContact',
          contactIndex: 0,
          timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000 + 60000).toISOString(),
          txHash: '2bQr2eOsU6vZcCnSt7qT8gDhE3yFjK0wM5zO1xV2yRs5',
          note: 'Juliana notificada por Telegram',
        },
        {
          type: 'WellbeingConfirmed',
          timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000 + 90000).toISOString(),
          txHash: '4cRs3fPtV7wAdDoUu8rU9hEiF4zGkL1xN6AP2yW3zSt6',
          note: 'Juliana confirmó: mamá se había agachado a buscar algo',
        },
        {
          type: 'Resolved',
          timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000 + 91000).toISOString(),
          txHash: '6dSt4gQuW8xBeEpVv9sV0iFjG5AHlM2yO7BQ3zX4ATu7',
        },
      ],
      resolved: true,
      resolvedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000 + 91000).toISOString(),
    },
  ],
}

export const mockAlert: DashboardData = {
  patientName: 'Carmen García',
  patientAge: 78,
  status: 'alert',
  vitals: {
    heartRate: 38,
    spo2: 94,
    skinTemp: 36.2,
    timestamp: new Date(Date.now() - 45 * 1000).toISOString(), // hace 45 segundos
  },
  activeEvent: {
    id: 'evt-003',
    type: 'LowHR',
    severity: 2,
    value: 38,
    timestamp: new Date(Date.now() - 45 * 1000).toISOString(),
    actions: [
      {
        type: 'GracePeriod',
        timestamp: new Date(Date.now() - 45 * 1000).toISOString(),
        txHash: '8eTu5hRvX9yCfFqWw0tW1jGkH6BImN3zP8CR4AY5BUv8',
        note: 'Esperando confirmación de bienestar',
      },
    ],
    resolved: false,
  },
  history: mockOk.history,
  graceSecondsRemaining: 60,
}

export const mockEmergency: DashboardData = {
  patientName: 'Carmen García',
  patientAge: 78,
  status: 'emergency',
  vitals: {
    heartRate: 38,
    spo2: 87,
    skinTemp: 35.8,
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(), // hace 3 minutos
  },
  activeEvent: {
    id: 'evt-004',
    type: 'LowSpO2',
    severity: 2,
    value: 87,
    timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
    actions: [
      {
        type: 'GracePeriod',
        timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(),
        txHash: '0fUv6iSwY0zDgGrXx1uX2kHlI7CJoO4AP9DS5BZ6CVw9',
        note: 'Esperando confirmación de bienestar',
      },
      {
        type: 'NotifiedContact',
        contactIndex: 0,
        timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
        txHash: '1gVw7jTxZ1AEhHsYy2vY3lImJ8DKpP5BQ0ET6CA7DWx0',
        note: 'Juliana notificada por Telegram',
      },
      {
        type: 'Escalated',
        contactIndex: 1,
        timestamp: new Date(Date.now() - 90 * 1000).toISOString(),
        txHash: '2hWx8kUyA2BFiItZz3wZ4mJnK9ELqQ6CR1FU7DB8EXy1',
        note: 'Marta (vecina) notificada por Telegram',
      },
      {
        type: 'Escalated',
        contactIndex: 2,
        timestamp: new Date(Date.now() - 60 * 1000).toISOString(),
        txHash: '3iXy9lVzB3CGjJuAA4xA5nKoL0FMrR7DS2GV8EC9FYz2',
        note: 'Llamando al servicio de emergencias',
      },
    ],
    resolved: false,
  },
  history: mockOk.history,
}
