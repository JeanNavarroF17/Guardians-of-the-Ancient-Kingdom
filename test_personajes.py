"""Pruebas automatizadas con Pytest (ejecución: pytest -v)."""

import pytest

from personajes import (Arquero, AtaqueInvalidoError, Combate, Guerrero, Mago,
                        Personaje)


# ---------- Creación ----------
def test_creacion_valida_de_los_tres_tipos():
    for clase in (Guerrero, Mago, Arquero):
        p = clase("Heroe", 100, 30, 10)
        assert isinstance(p, Personaje)
        assert (p.nombre, p.vida, p.ataque, p.defensa) == ("Heroe", 100, 30, 10)


def test_personaje_es_abstracto():
    with pytest.raises(TypeError):
        Personaje("X", 10, 10, 10)


# ---------- Rechazo de valores ----------
@pytest.mark.parametrize("vida", [-1, 101, 1000])
def test_vida_fuera_de_rango(vida):
    with pytest.raises(ValueError):
        Guerrero("A", vida, 10, 5)


@pytest.mark.parametrize("nombre", ["", "   "])
def test_nombre_vacio(nombre):
    with pytest.raises(ValueError):
        Mago(nombre, 50, 10, 5)


@pytest.mark.parametrize("ataque", [0, -5])
def test_ataque_invalido(ataque):
    with pytest.raises(ValueError):
        Arquero("A", 50, ataque, 5)


def test_defensa_negativa():
    with pytest.raises(ValueError):
        Guerrero("A", 50, 10, -1)


def test_tipos_incorrectos():
    with pytest.raises(TypeError):
        Mago("A", "50", 10, 5)
    with pytest.raises(TypeError):
        Mago(123, 50, 10, 5)


def test_setters_validan():
    p = Guerrero("A", 50, 10, 5)
    with pytest.raises(ValueError):
        p.vida = 150
    p.vida = 80
    assert p.vida == 80


# ---------- Daño de cada clase ----------
def test_dano_guerrero():
    g = Guerrero("G", 100, 30, 20)
    objetivo = Mago("M", 100, 10, 10)
    assert g.atacar(objetivo) == 26
    assert objetivo.vida == 74


def test_guerrero_redondea_hacia_abajo():
    g = Guerrero("G", 100, 11, 5)  # 11 * 1.2 = 13.2 -> 13 - 5 = 8
    assert g.calcular_danio(Mago("M", 100, 10, 5)) == 8


def test_dano_mago_ignora_defensa():
    m = Mago("M", 80, 40, 10)
    objetivo = Guerrero("G", 100, 10, 20)
    assert m.atacar(objetivo) == 40


def test_dano_arquero_critico():
    a = Arquero("A", 90, 35, 15)
    objetivo = Guerrero("G", 100, 10, 15)
    assert a.atacar(objetivo) == 40


def test_arquero_sin_dano_si_ataque_no_supera_defensa():
    a = Arquero("A", 90, 10, 15)
    assert a.atacar(Guerrero("G", 100, 10, 15)) == 0
    a2 = Arquero("A2", 90, 15, 15)
    assert a2.atacar(Guerrero("G", 100, 10, 15)) == 0


# ---------- Vida nunca negativa ----------
def test_vida_nunca_negativa():
    p = Guerrero("P", 20, 10, 5)
    assert p.recibir_danio(50) == 20
    assert p.vida == 0
    assert not p.esta_vivo()


def test_danio_negativo_rechazado():
    with pytest.raises(ValueError):
        Guerrero("P", 20, 10, 5).recibir_danio(-1)


# ---------- Derrotado no ataca ----------
def test_derrotado_no_puede_atacar():
    muerto = Mago("Muerto", 10, 30, 5)
    muerto.recibir_danio(10)
    with pytest.raises(AtaqueInvalidoError):
        muerto.atacar(Guerrero("V", 50, 10, 5))


def test_no_se_puede_atacar_a_derrotado_ni_a_none():
    vivo = Guerrero("V", 50, 10, 5)
    muerto = Mago("M", 10, 30, 5)
    muerto.recibir_danio(10)
    with pytest.raises(AtaqueInvalidoError):
        vivo.atacar(muerto)
    with pytest.raises(AtaqueInvalidoError):
        vivo.atacar(None)


# ---------- Combate ----------
def test_combate_ejemplo_del_enunciado():
    arthas = Guerrero("Arthas", 100, 30, 20)
    gandalf = Mago("Gandalf", 80, 40, 10)
    combate = Combate(arthas, gandalf, verbose=False)
    assert combate.iniciar() is gandalf
    assert arthas.vida == 0
    assert gandalf.vida == 2
    assert not combate.empate


def test_combate_empate_tecnico():
    a1 = Arquero("A", 100, 10, 50)
    a2 = Arquero("B", 100, 10, 50)
    combate = Combate(a1, a2, verbose=False)
    assert combate.iniciar() is None
    assert combate.empate
    assert combate.rondas == 1


def test_combate_requiere_personajes_distintos_y_validos():
    g = Guerrero("G", 100, 10, 5)
    with pytest.raises(ValueError):
        Combate(g, g)
    with pytest.raises(TypeError):
        Combate(g, "no soy personaje")


def test_cambiar_turno_alterna():
    g = Guerrero("G", 100, 10, 5)
    m = Mago("M", 100, 10, 5)
    c = Combate(g, m, verbose=False)
    assert c.atacante_actual is g
    c.cambiar_turno()
    assert c.atacante_actual is m
    c.cambiar_turno()
    assert c.atacante_actual is g
