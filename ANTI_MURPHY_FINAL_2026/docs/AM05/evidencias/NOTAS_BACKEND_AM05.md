# AM-05 — backend: contrato e verificação

Arquivos próprios: `atelier/service.py`, novo `atelier/analysis_provenance.py`, novo `tests/test_am05_provenance.py`.

Reprodução antes: `backend/before.json` confirma Goal0/100 ->18/1 pontos com mesma assinatura global e duração idêntica após troca de seleção com assinatura global diferente. O campo legado global permanece metadado; a correção usa contextos específicos e assinatura determinística.

## Contrato

- `info.analysis_contexts`:12 chaves `lab:*`/`advanced:*`, valores compactos contendo somente `context_signature`. Não duplica modelo12vezes no payload de estado.
- Resultado `provenance`: schemaam05-v2; scope,mode,context_key,context_signature; inputsnormalizados; dependenciesimutáveis (modelo/pedidos/parâmetros); assinatura determinística; project_id/project_name/source/run_id/calculated_atmetadados.
- Assinatura final = SHA256 de context_signature+inputs. Hora, run_id, nome do projeto e source não fazem parte da configuração numérica.
- Global analysis_signature continua disponível em info, dashboards e auditoria para proteção de respostas agregadas assíncronas.
- Diagnóstico conserva bottleneck do resultado de origem para não misturar cabeçalho atual com tabela histórica.

## Dependências

Todos os contextos incluem projeto, modelo, ordem explícita dos postos e carteira. A ordem dos postos influencia seleção aleatória e enumeração finita.

| Família | Dependências adicionais |
|---|---|
| labduration | regra,semente,posto/iníciofalha; duração é varrida internamente |
| labdispatch | semente,posto/início/duraçãofalha; regra é varrida internamente |
| labrobustness | regra,incidente,ação temporal selecionada e investimento; sementes700–705 fixas |
| labstress | regra,configuração fixa de perturbações/semente2026; ignorafalha/sementeatual |
| labcapacity | nominal(regra,semente),limitesbusca; controlesSLA/TP |
| labgoal | nominal,incidente,políticacompleta,delay; controleSLA; seleçãoirrelevante |
| advanceddiagnostic | nominal+incidente |
| advancedopportunities | nominal,maxcandidates28 |
| advancedsensitivity | nominal,maxadd3; controlesposto/recurso |
| advanceddemand | nominal,faixademanda; controleSLA |
| advanceduncertainty | modelo,regra,incidente;12sementes2100+ fixas |
| advancedrecovery | nominal,incidente,delay,maxresults8 |

## Testes

40 testes novos aprovados. Junto aos79 testesAM11 sem testeJS opcional:119 aprovados4,57s. Log `backend/focused-final.log`.

Cobertura: modelos/pedidos; sementesfixas/variáveis; incidenteseirrelevância nominal; seleçãorelevanteapenaspareado; parâmetros/defaults; normalização80/80.0; timestampsindependentes; cloneprojeto; nomeprojetometadado; origemimutável;12modos; snapshotsagregados; info sem motor.

Nenhuma fórmula, semente de simulação, enumeração ou tratamento de inviabilidade foi alterado. AM09/10 e demais problemas mantidos fora do escopo.
