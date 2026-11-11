"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.assertBundle = assertBundle;
/** At the trust boundary validate in Python with ComparisonBundle.model_validate_json. */
function assertBundle(value) {
    if (!value || typeof value !== 'object')
        throw new Error('Pacote de dados ausente.');
    const obj = value;
    if (obj.schema_version !== '1.1.0' || !obj.definition || !obj.topology || !obj.common_history || !obj.branch_A || !obj.branch_B) {
        throw new Error('Contrato incompatível. Necessário ComparisonBundle v1.1.0 completo.');
    }
    const def = obj.definition;
    if (!def.stations || Array.isArray(def.stations))
        throw new Error('definition.stations deve ser um objeto indexado por ID.');
    const common = obj.common_history;
    if (!Array.isArray(common.events) || !Array.isArray(common.keyframes))
        throw new Error('Histórico comum incompleto.');
}
