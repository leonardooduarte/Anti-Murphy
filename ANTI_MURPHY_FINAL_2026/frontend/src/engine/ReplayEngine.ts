import type { BranchId, ComparisonBundle, EventDelta, SimulationSnapshot } from '../types/simulation_contract';
import { assertBundle } from '../types/simulation_contract';
const branchSnapshot = (s: SimulationSnapshot, branch: 'A'|'B'): SimulationSnapshot => ({ ...s, branch_id: branch });
function apply(state:SimulationSnapshot, e:EventDelta):SimulationSnapshot {
  if (e.seq !== state.seq + 1 || e.time_us < state.time_us) throw new Error(`Delta fora de ordem: ${e.seq}`);
  return {branch_id:state.branch_id,seq:e.seq,time_us:e.time_us,
    stations:{...state.stations,...e.station_upserts},
    units:{...state.units,...e.unit_upserts},orders:{...state.orders,...e.order_upserts}};
}
/** Pure deterministic seek; do not interpolate operational status or cost. */
export class ReplayEngine {
  static computeStateAtTime(bundle: ComparisonBundle, targetTimeUs: number, branch: 'A'|'B'):SimulationSnapshot {
    assertBundle(bundle);
    if (!Number.isSafeInteger(targetTimeUs) || targetTimeUs < 0) throw new Error('Tempo inválido');
    const common = bundle.common_history;
    const inCommon = targetTimeUs < bundle.fork.time_us;
    const trail = inCommon ? common : bundle[`branch_${branch}`];
    let base:SimulationSnapshot = inCommon ? common.keyframes[0] : branchSnapshot(common.keyframes.at(-1)!,branch);
    if (!base) throw new Error('Keyframe inicial ausente');
    // Keyframes are complete state AFTER seq. Prefer last by event ordering at equal time.
    for (const kf of (inCommon ? common.keyframes : trail.keyframes)) {
      if (kf.time_us <= targetTimeUs && kf.seq >= base.seq) base = kf;
    }
    for (const e of trail.events) {
      if (e.seq > base.seq && e.time_us <= targetTimeUs) base = apply(base,e);
    }
    return base.branch_id === branch ? base : branchSnapshot(base,branch);
  }
  static maxTimeUs(bundle: ComparisonBundle):number {
    const end = (branch:'A'|'B') => {
      const b=bundle[`branch_${branch}`];
      return Math.max(b.summary.makespan_us ?? 0, b.events.at(-1)?.time_us ?? 0, b.keyframes.at(-1)?.time_us ?? 0);
    };
    return Math.max(end('A'),end('B'));
  }
  static markers(bundle:ComparisonBundle):Array<{t:number;label:string;kind:'incident'|'decision'|'effect'}> {
    const out: Array<{t:number;label:string;kind:'incident'|'decision'|'effect'}> = [
      {t:bundle.incident.start_us,label:'Falha',kind:'incident'},
      {t:bundle.fork.time_us,label:'Decisão',kind:'decision'},
    ];
    const eff=bundle.branch_B.action?.effective_us;
    if(eff !== null && eff !== undefined)out.push({t:eff,label:'Ação efetiva',kind:'effect'});
    return out;
  }
}
