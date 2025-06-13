from collections import defaultdict
import subprocess

def get_group_members(groups: list[str]) -> dict[str, list[str]]:
  """
  Retrieve a dictionary mapping group names to their users.

  Parameters
  ----------
  groups : list[str]
    List of group names to query.

  Returns
  -------
  dict[str, list[str]]
    Dictionary where keys are group names and values are lists of users.
  """
  group_dict = defaultdict(list)
  for group in groups:
    if (output:= subprocess.check_output(["getent", "group", group], text=True).strip()):
      parts = output.split(":")
      members = parts[3].split(",") if len(parts) > 3 and parts[3] else []
      group_dict[group] = members
    else:
      group_dict[group] = []

  return group_dict

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python get_group_members.py <group1> <group2> ...")
        sys.exit(1)
    
    groups = sys.argv[1:]
    members = get_group_members(groups)
    for group, users in members.items():
        print(f"{group}: {', '.join(users) if users else 'No members'}")