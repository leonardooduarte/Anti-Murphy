/** Mirrors Python ComparisonBundle 1.1.0. All upserts are COMPLETE entity states. */
export type BranchId = 'common' | 'A' | 'B';
export type StationStatus = 'idle' | 'running' | 'down' | 'blocked' | 'setup';
export interface StationDefinition { id: string; name: string; machine_ids: string[]; required_skills: string[]; buffer_capacity: number | null; x: number; y: number; }
export interface OrderDefinition { id: string; quantity: number; due_us: number; route_station_ids: string[]; }
export interface StationState { id: string; status: StationStatus; machine_capacity: number; workers_available: number; busy_slots: number; queue_unit_ids: string[]; processing_unit_ids: string[]; paused_unit_ids: string[]; }
export interface UnitState { id: string; order_id: string; route_step: number; station_id: string | null; machine_id: string | null; phase: 'unreleased'|'queued'|'processing'|'paused'|'completed'|'blocked'; }
export interface OrderState { id: string; completed_units: number; completion_us: number | null; }
export interface SimulationSnapshot { branch_id: BranchId; seq: number; time_us: number; stations: Record<string, StationState>; units: Record<string, UnitState>; orders: Record<string, OrderState>; }
export type EventKind = 'queue_enter'|'queue_leave'|'operation_start'|'operation_pause'|'operation_resume'|'operation_finish'|'outage_start'|'outage_end'|'resource_changed'|'setup_start'|'setup_finish'|'order_completed'|'action_applied'|'model_blocked';
export interface EventDelta { seq: number; time_us: number; kind: EventKind; entity_id: string|null; station_upserts: Record<string, StationState>; unit_upserts: Record<string, UnitState>; order_upserts: Record<string, OrderState>; }
export interface HistoryBranch { keyframes: SimulationSnapshot[]; events: EventDelta[]; provenance: 'engine_native'|'trace_derived'|'synthetic_fixture'; }
export interface ConstraintCheck { name: string; status: 'pass'|'fail'|'unknown'; subject_id: string|null; evidence: string; }
export interface BranchSummary { feasible: 'feasible'|'infeasible'|'unverified'; checks: ConstraintCheck[]; total_cost_cents: number|null; sla_pct: number|null; makespan_us: number|null; late_orders: number|null; }
export interface BranchTimeline extends HistoryBranch { branch_id:'A'|'B'; run_id:string; scenario_label:string; model_sha256:string; seed:number; action: {action_id:string; label:string; requested_us:number; effective_us:number|null;}|null; summary:BranchSummary; }
export interface ComparisonBundle {
  schema_version: '1.1.0'; experiment_id:string;
  time_unit:'simulated_microsecond'; time_origin:'simulation_start';
  definition:{ stations:Record<string,StationDefinition>; orders:Record<string,OrderDefinition> };
  topology:{ edges:Array<{source:string;target:string;waypoints:Array<{x:number;y:number}>}>;transport_semantics:'logical_instantaneous' };
  incident:{incident_id:string;station_id:string;start_us:number;planned_end_us:number};
  fork:{seq:number;time_us:number;reason:string};
  common_history:HistoryBranch; branch_A:BranchTimeline; branch_B:BranchTimeline;
}
/** At the trust boundary validate in Python with ComparisonBundle.model_validate_json. */
export function assertBundle(value: unknown): asserts value is ComparisonBundle {
  if (!value || typeof value !== 'object') throw new Error('Pacote de dados ausente.');
  const obj = value as Record<string, unknown>;
  if (obj.schema_version !== '1.1.0' || !obj.definition || !obj.topology || !obj.common_history || !obj.branch_A || !obj.branch_B) {
    throw new Error('Contrato incompatível. Necessário ComparisonBundle v1.1.0 completo.');
  }
  const def = obj.definition as Record<string, unknown>;
  if (!def.stations || Array.isArray(def.stations)) throw new Error('definition.stations deve ser um objeto indexado por ID.');
  const common = obj.common_history as Record<string, unknown>;
  if (!Array.isArray(common.events) || !Array.isArray(common.keyframes)) throw new Error('Histórico comum incompleto.');
}
