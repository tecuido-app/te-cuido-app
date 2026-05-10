// =============================================================
// TE CUIDO — Smart Contract Anchor
// Audit log on-chain de cada acción del agente.
//
// Deploy: copiar este archivo a Solana Playground (https://beta.solpg.io)
// → Build → Deploy. Reemplazar PROGRAM_ID en declare_id! por el real.
// =============================================================

use anchor_lang::prelude::*;

declare_id!("FL87A7UXXJGwj8ra3RYUNHHSBSdp9ML3VL9TjfMBpMWN");

#[program]
pub mod tecuido {
    use super::*;

    /// Crea un nuevo EventLog cuando el detector encuentra una anomalía.
    /// event_id es generado por el cliente (ej: timestamp en ms) — sirve para PDA único.
    pub fn register_event(
        ctx: Context<RegisterEvent>,
        event_id: u64,
        event_type: u8,    // 0=Fall, 1=LowHR, 2=LowSpO2
        severity: u8,      // 1..3
        value: i64,        // valor que disparó la alerta
    ) -> Result<()> {
        let log = &mut ctx.accounts.event_log;
        log.event_id = event_id;
        log.event_type = event_type;
        log.severity = severity;
        log.value = value;
        log.timestamp = Clock::get()?.unix_timestamp;
        log.action_count = 0;
        log.resolved = false;
        log.resolved_at = 0;
        log.bump = ctx.bumps.event_log;
        Ok(())
    }

    /// Agrega una acción del agente al EventLog (notificación, escalada, etc).
    pub fn register_action(
        ctx: Context<UpdateEvent>,
        action_type: u8,    // 0=GracePeriod, 1=AIDismissed, 2=Notified, 3=Escalated, 4=Wellbeing, 5=Resolved
        contact_index: u8,
    ) -> Result<()> {
        let log = &mut ctx.accounts.event_log;
        require!((log.action_count as usize) < log.actions.len(), ErrorCode::TooManyActions);

        let i = log.action_count as usize;
        log.actions[i] = StoredAction {
            action_type,
            contact_index,
            timestamp: Clock::get()?.unix_timestamp,
        };
        log.action_count += 1;
        Ok(())
    }

    /// Marca el evento como resuelto (familiar confirmó que la paciente está bien).
    pub fn confirm_wellbeing(ctx: Context<UpdateEvent>) -> Result<()> {
        let log = &mut ctx.accounts.event_log;
        log.resolved = true;
        log.resolved_at = Clock::get()?.unix_timestamp;
        Ok(())
    }
}

// ============================================================
// Cuentas
// ============================================================

#[derive(Accounts)]
#[instruction(event_id: u64)]
pub struct RegisterEvent<'info> {
    #[account(
        init,
        payer = signer,
        space = 8 + EventLog::SIZE,
        seeds = [b"event", &event_id.to_le_bytes()],
        bump
    )]
    pub event_log: Account<'info, EventLog>,
    #[account(mut)]
    pub signer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdateEvent<'info> {
    #[account(mut)]
    pub event_log: Account<'info, EventLog>,
    pub signer: Signer<'info>,
}

// ============================================================
// Estado on-chain
// ============================================================

#[account]
pub struct EventLog {
    pub event_id: u64,
    pub event_type: u8,
    pub severity: u8,
    pub value: i64,
    pub timestamp: i64,
    pub actions: [StoredAction; 10],   // hasta 10 acciones por evento
    pub action_count: u8,
    pub resolved: bool,
    pub resolved_at: i64,
    pub bump: u8,
}

impl EventLog {
    // 8 (event_id) + 1 + 1 + 8 + 8 + (10 * 10) + 1 + 1 + 8 + 1
    pub const SIZE: usize = 8 + 1 + 1 + 8 + 8 + (10 * StoredAction::SIZE) + 1 + 1 + 8 + 1;
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, Default)]
pub struct StoredAction {
    pub action_type: u8,
    pub contact_index: u8,
    pub timestamp: i64,
}

impl StoredAction {
    pub const SIZE: usize = 1 + 1 + 8;
}

// ============================================================
// Errores
// ============================================================

#[error_code]
pub enum ErrorCode {
    #[msg("Too many actions on this event (max 10)")]
    TooManyActions,
}
