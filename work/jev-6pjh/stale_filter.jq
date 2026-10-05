[
  .[]
  | select(.ts >= $start and .ts < $end)
  | select(
      ((.reason // "") + " " + (.error // "") + " " + (.status // ""))
      | test("permission-required|recipient-and-data-class")
    )
]
| length
