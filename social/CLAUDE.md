# Regras para trabalhar no Instagram do Cortexplor

Vale para qualquer sessão, thread ou Routine que mexa em `social/` ou `scripts/social/`. Leia também `social/INSTAGRAM.md`.

1. **Branch.** Todo o trabalho do Instagram fica no branch `instagram`. Não misturar com o `main` sem o dono pedir. A Routine do site continua só no `main`.
2. **Estilos são travados.** Os 8 estilos aprovados (`scripts/social/styles_a.py`, `styles_b.py`) só mudam se o dono pedir uma mudança visual. Qualquer alteração nesses arquivos exige rodar `python scripts/social/check.py golden`; se algum estilo "mudou" sem o dono ter pedido, desfaça. Só regrave as referências (`golden --update`) com aprovação explícita do dono.
3. **Nada sai sem passar no controle.** Para cada matéria: `python scripts/social/check.py build <slug>` precisa terminar sem erro (roda `redacao.py check`: spec, legenda e encaixe; depois a análise da foto). Se reprovar, corrija o texto (encurte) e rode de novo; não entregue carrossel reprovado nem "ajuste" o limite para passar.
4. **Texto.** Segue a skill `voz-cortexplor`: fato na primeira frase, só o que está nos fatos confirmados da matéria, atribuição, nenhum dado inventado, sem opinião. Limites de tamanho em `check.py` (constantes no topo).
5. **Fotos.** Mantêm a cor original. Foto muito escura tira o estilo `meiatinta` do rodízio da matéria (já automático em `eligible_styles`). Foto pequena gera aviso.
6. **Legenda.** Segue o padrão da seção 4 de `social/INSTAGRAM.md`: sem link, até 4 hashtags com `#cortexplor`, chamada final alternando A/B, texto alternativo nos 6 slides. `check.py` valida.
7. **Rodízio.** Estilo escolhido por `rotation.pick_styles`, nunca repetindo em sequência, usando apenas os estilos elegíveis da matéria.
8. **Aprovação manual.** Enquanto o dono não liberar o automático, todo carrossel fica "pendente de aprovação" e nada é publicado. Publicação pela API só depois de aprovação explícita por carrossel.
9. **Contas.** Português e inglês são contas separadas; texto de uma não é tradução literal da outra.
