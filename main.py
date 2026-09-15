"""
Converte o JSON de "Iniciativas" do Parlamento (app.parlamento.pt) em CSVs
relacionados: iniciativas.csv, eventos.csv, votacoes.csv, intervencoes.csv.

Uso:
    1) Buscar o JSON (como no teu script original) e guardar em disco, OU
       usar diretamente a partir da resposta `r.json()`.
    2) Correr: python parlamento_to_csv.py caminho_para_o_ficheiro.json

O parser é tolerante a campos em falta (usa sempre .get()), porque nem
todas as iniciativas têm a mesma "forma" (autores, votações, etc. variam).
"""

import csv
import json
import sys
from pathlib import Path


def get_autor(ini: dict) -> str:
    """Resume o(s) autor(es) da iniciativa numa única string."""
    partes = []

    outros = ini.get("IniAutorOutros")
    if outros:
        nome = outros.get("nome")
        sigla = outros.get("sigla")
        partes.append(f"{nome} ({sigla})" if sigla else nome)

    grupos = ini.get("IniAutorGruposParlamentares")
    if grupos:
        for g in grupos:
            sigla = g.get("GP") or g.get("sigla")
            if sigla:
                partes.append(sigla)

    deputados = ini.get("IniAutorDeputados")
    if deputados:
        for d in deputados:
            nome = d.get("nome")
            if nome:
                partes.append(nome)

    return "; ".join(p for p in partes if p)


def ultima_fase(eventos: list) -> tuple[str, str]:
    """Devolve (nome_da_ultima_fase, data_da_ultima_fase) por ordem de DataFase."""
    if not eventos:
        return "", ""
    com_data = [e for e in eventos if e.get("DataFase")]
    if not com_data:
        return "", ""
    ultimo = max(com_data, key=lambda e: e["DataFase"])
    return ultimo.get("Fase", ""), ultimo.get("DataFase", "")


def extrair_votos(sigla_lista) -> str:
    if not sigla_lista:
        return ""
    if isinstance(sigla_lista, list):
        return "; ".join(str(x) for x in sigla_lista)
    return str(sigla_lista)


def main(json_path: str):
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        # alguns endpoints devolvem {"IniciativasXVII": [...]} em vez de lista direta
        data = next((v for v in data.values() if isinstance(v, list)), [data])

    iniciativas_rows = []
    eventos_rows = []
    votacoes_rows = []
    intervencoes_rows = []

    for ini in data:
        ini_id = ini.get("IniId") or ini.get("IniNr") or ""
        eventos = ini.get("IniEventos") or []

        fase_nome, fase_data = ultima_fase(eventos)

        iniciativas_rows.append({
            "IniId": ini_id,
            "IniLeg": ini.get("IniLeg", ""),
            "IniNr": ini.get("IniNr", ""),
            "IniTipo": ini.get("IniDescTipo") or ini.get("IniTipo", ""),
            "IniTitulo": ini.get("IniTitulo") or ini.get("IniEpigrafe", ""),
            "Autor": get_autor(ini),
            "DataInicioLegislatura": ini.get("DataInicioleg", ""),
            "DataFimLegislatura": ini.get("DataFimleg", ""),
            "UltimaFase": fase_nome,
            "DataUltimaFase": fase_data,
            "NumEventos": len(eventos),
            "NumAnexos": len(ini.get("IniAnexos") or []),
        })

        for ev in eventos:
            evt_id = ev.get("EvtId", "")
            eventos_rows.append({
                "IniId": ini_id,
                "EvtId": evt_id,
                "OevId": ev.get("OevId", ""),
                "CodigoFase": ev.get("CodigoFase", ""),
                "Fase": ev.get("Fase", ""),
                "DataFase": ev.get("DataFase", ""),
                "Observacao": ev.get("ObsFase", ""),
            })

            votacao = ev.get("Votacao")
            if votacao:
                for v in votacao:
                    votacoes_rows.append({
                        "IniId": ini_id,
                        "EvtId": evt_id,
                        "Fase": ev.get("Fase", ""),
                        "DataFase": ev.get("DataFase", ""),
                        "Resultado": v.get("resultado", ""),
                        "Detalhe": v.get("detalhe", ""),
                        "Favor": extrair_votos(v.get("favor")),
                        "Contra": extrair_votos(v.get("contra")),
                        "Abstencao": extrair_votos(v.get("abstencao")),
                    })

            debates = ev.get("Intervencoesdebates")
            if debates:
                for d in debates:
                    data_reuniao = d.get("dataReuniaoPlenaria", "")
                    for orador in d.get("oradores") or []:
                        deputados = orador.get("deputadosOradores") or [{}]
                        membro_gov = orador.get("membrosGoverno") or {}
                        for dep in deputados:
                            intervencoes_rows.append({
                                "IniId": ini_id,
                                "EvtId": evt_id,
                                "DataReuniao": data_reuniao,
                                "GrupoParlamentar": dep.get("GP", ""),
                                "Deputado": dep.get("nome", ""),
                                "MembroGoverno": membro_gov.get("nome", ""),
                                "CargoGoverno": membro_gov.get("cargo", ""),
                                "HoraInicio": orador.get("horaInicio", ""),
                                "HoraTermo": orador.get("horaTermo", ""),
                                "Sumario": orador.get("sumario", ""),
                            })

    def write_csv(filename, rows):
        if not rows:
            print(f"(sem dados para {filename})")
            return
        fieldnames = list(rows[0].keys())
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Escrito {filename} ({len(rows)} linhas)")

    write_csv("data/iniciativas.csv", iniciativas_rows)
    write_csv("data/eventos.csv", eventos_rows)
    write_csv("data/votacoes.csv", votacoes_rows)
    write_csv("data/intervencoes.csv", intervencoes_rows)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python parlamento_to_csv.py caminho_para_o_ficheiro.json")
        sys.exit(1)
    main(sys.argv[1])