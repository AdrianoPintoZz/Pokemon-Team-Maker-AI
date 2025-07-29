import pandas as pd
import streamlit as st
from collections import Counter


@st.cache_data
def load_data():
    df = pd.read_csv("Pokemon.csv")
    df = df[~df["Name"].str.contains(r'(.+)mega \1', case=False, na=False)]
    df["Name"] = df["Name"].str.strip().str.lower()
    return df


df_original = load_data()

st.title("Pokemon Team Generator")


geracao_escolhida = st.selectbox("Choose the generation:", sorted(df_original["Generation"].unique()))
df = df_original[df_original["Generation"] == geracao_escolhida]

iniciais_por_geracao = {
    1: {"Bulbasaur": "Venusaur", "Charmander": "Charizard", "Squirtle": "Blastoise"},
    2: {"Chikorita": "Meganium", "Cyndaquil": "Typhlosion", "Totodile": "Feraligatr"},
    3: {"Treecko": "Sceptile", "Torchic": "Blaziken", "Mudkip": "Swampert"},
    4: {"Turtwig": "Torterra", "Chimchar": "Infernape", "Piplup": "Empoleon"},
    5: {"Snivy": "Serperior", "Tepig": "Emboar", "Oshawott": "Samurott"},
    6: {"Chespin": "Chesnaught", "Fennekin": "Delphox", "Froakie": "Greninja"},
}

iniciais = iniciais_por_geracao.get(geracao_escolhida, {})
if not iniciais:
    st.warning("Ainda não foram definidos iniciais para esta geração.")
    st.stop()

inicial = st.selectbox("Choose your initial pokemon:", list(iniciais.keys()))
evolucao_inicial = iniciais[inicial]


df["Name"] = df["Name"].str.strip().str.lower()
evolucao_inicial = evolucao_inicial.strip().lower()

pokemon_fixo = df[df["Name"] == evolucao_inicial]

if pokemon_fixo.empty:
    st.error(f"O Pokémon evoluído '{evolucao_inicial.title()}' não foi encontrado para a geração {geracao_escolhida}.")
    st.stop()

df = df[df["Name"] != evolucao_inicial]


tipos_disponiveis = pd.unique(df[['Type 1', 'Type 2']].values.ravel('K'))
tipos_disponiveis = [t for t in tipos_disponiveis if pd.notna(t)]
tipos_preferidos = st.multiselect("🧪 Preferable stats for team:", sorted(tipos_disponiveis))

stats = ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
stats_prioritarias = st.multiselect(
    "📊 Estatísticas prioritárias (opcional, escolha até 2):",
    stats,
    max_selections=2
)


incluir_lendarios = st.checkbox("🧬 Include legendary pokemons?", value=False)

if st.button("🔍 Generate Team"):

    equipa_base = df.copy()


    if not incluir_lendarios and "Legendary" in equipa_base.columns:
        equipa_base = equipa_base[equipa_base["Legendary"] == False]

    iniciais_excluidos = set(iniciais.values()) - {evolucao_inicial}
    equipa_base = equipa_base[~equipa_base["Name"].isin(iniciais_excluidos)]


    if tipos_preferidos:
        equipa_base = equipa_base[
            equipa_base["Type 1"].isin(tipos_preferidos) |
            equipa_base["Type 2"].isin(tipos_preferidos)
        ]

    if stats_prioritarias:
        equipa_base["SCORE"] = equipa_base[stats_prioritarias].sum(axis=1)
        equipa_base = equipa_base.sort_values(by="SCORE", ascending=False)
    else:
        equipa_base = equipa_base.sort_values(by="Total", ascending=False)


    equipa_final = [pokemon_fixo.iloc[0]]
    tipos_usados = set(pokemon_fixo[["Type 1", "Type 2"]].values.flatten())


    equipa_final = [pokemon_fixo.iloc[0]]

    tipos_usados = Counter(pokemon_fixo[["Type 1", "Type 2"]].values.flatten())

    for _, row in equipa_base.iterrows():
        tipos_pokemon = [row["Type 1"], row["Type 2"]]

        if all(tipos_usados.get(tipo, 0) < 2 for tipo in tipos_pokemon if pd.notna(tipo)):
            equipa_final.append(row)
            tipos_usados.update(tipos_pokemon)

        if len(equipa_final) == 6:
            break

    equipa_final = pd.DataFrame(equipa_final)


    st.subheader("Final Team:")
    st.markdown("""
    <style>
    .custom-table th:first-child,
    .custom-table td:first-child {
        min-width: 150px;
        white-space: nowrap;
    }
    .custom-table td {
        padding: 6px 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        equipa_final[["Name", "Type 1", "Type 2", "Total", "HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed", "Generation"]]
        .to_html(index=False, classes="custom-table"),
        unsafe_allow_html=True
    )
    st.success("Team generated successfully! Good Luck on your journey🎉")
