"""Interactive text demonstration using Ayeon's cognition boundary."""

from __future__ import annotations

from ayeon.contracts.common import HealthState, TraceContext
from ayeon.contracts.state import AyeonStateSnapshot
from ayeon.core.cognition.coordinator import CognitionCoordinator
from ayeon.core.context.builder import ContextBuilder
from ayeon.demo_cognition import DemoCognitionEngine


def main() -> None:
    coordinator = CognitionCoordinator(
        context_builder=ContextBuilder(),
        cognition_engine=DemoCognitionEngine(),
    )
    sequence = 0

    print("Ayeon · demo de conversación por texto")
    print("Escribe hola, ayuda o salir.")

    while True:
        try:
            message = input("\nTú> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAyeon> Hasta luego.")
            break

        if message.casefold() == "salir":
            print("Ayeon> Hasta luego.")
            break

        if not message:
            continue

        sequence += 1
        output = coordinator.process(
            trace=TraceContext.root(),
            user_input=message,
            state_snapshot=AyeonStateSnapshot(
                sequence=sequence,
                runtime_health=HealthState.HEALTHY,
            ),
        )
        print(f"Ayeon> {output.spoken_response}")


if __name__ == "__main__":
    main()
