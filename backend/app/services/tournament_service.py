import math
import uuid
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class TournamentStage(Enum):
    REGISTRATION = "registration"
    SEEDING = "seeding"
    IN_PROGRESS = "in_progress"
    FINALS = "finals"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TournamentFormat(Enum):
    SINGLE_ELIMINATION = "single_elimination"
    DOUBLE_ELIMINATION = "double_elimination"
    ROUND_ROBIN = "round_robin"
    SWISS = "swiss"

@dataclass
class TournamentTeam:
    team_id: str
    team_name: str
    captain_profile_id: str
    roster_profile_ids: List[str]
    seed_index: int = 0
    wins: int = 0
    losses: int = 0
    points_differential: int = 0
    is_eliminated: bool = False

@dataclass
class TournamentMatchNode:
    match_id: str
    round_number: int
    bracket_index: int
    team_alpha_id: Optional[str] = None
    team_omega_id: Optional[str] = None
    winner_team_id: Optional[str] = None
    score_alpha: int = 0
    score_omega: int = 0
    scheduled_start: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    next_match_id: Optional[str] = None
    loser_bracket_match_id: Optional[str] = None

class TournamentManagerService:
    def __init__(self, tournament_id: str, title: str, max_teams: int = 16, format_type: TournamentFormat = TournamentFormat.SINGLE_ELIMINATION):
        self.tournament_id = tournament_id
        self.title = title
        self.max_teams = max_teams
        self.format_type = format_type
        self.stage = TournamentStage.REGISTRATION
        self.registered_teams: Dict[str, TournamentTeam] = {}
        self.bracket_tree: Dict[str, TournamentMatchNode] = {}
        self.prize_pool_credits: int = 500000
        self.prize_pool_shards: int = 10000

    def register_team(self, team: TournamentTeam) -> bool:
        if self.stage != TournamentStage.REGISTRATION:
            return False
        if len(self.registered_teams) >= self.max_teams:
            return False
        if team.team_id in self.registered_teams:
            return False

        self.registered_teams[team.team_id] = team
        return True

    def seed_teams_by_rating(self, team_ratings: Dict[str, float]):
        sorted_teams = sorted(
            self.registered_teams.values(),
            key=lambda t: team_ratings.get(t.team_id, 1000.0),
            reverse=True
        )
        for idx, team in enumerate(sorted_teams):
            team.seed_index = idx + 1
        self.stage = TournamentStage.SEEDING

    def generate_single_elimination_bracket(self) -> List[TournamentMatchNode]:
        num_teams = len(self.registered_teams)
        if num_teams < 2:
            raise ValueError("Not enough teams to generate bracket.")

        total_rounds = math.ceil(math.log2(num_teams))
        power_of_two = 2 ** total_rounds

        # Standard tournament pairing (1 vs 16, 8 vs 9, etc.)
        def get_seed_pairings(num_slots: int) -> List[int]:
            if num_slots == 2:
                return [1, 2]
            prev = get_seed_pairings(num_slots // 2)
            res = []
            for s in prev:
                res.append(s)
                res.append(num_slots + 1 - s)
            return res

        pairings = get_seed_pairings(power_of_two)
        teams_by_seed = {t.seed_index: t.team_id for t in self.registered_teams.values()}

        round_1_matches = []
        for i in range(0, len(pairings), 2):
            match_id = f"R1_M{i//2 + 1}_{uuid.uuid4().hex[:6]}"
            seed1 = pairings[i]
            seed2 = pairings[i + 1]

            node = TournamentMatchNode(
                match_id=match_id,
                round_number=1,
                bracket_index=i // 2,
                team_alpha_id=teams_by_seed.get(seed1),
                team_omega_id=teams_by_seed.get(seed2)
            )
            # Handle byes
            if node.team_alpha_id and not node.team_omega_id:
                node.winner_team_id = node.team_alpha_id
            elif node.team_omega_id and not node.team_alpha_id:
                node.winner_team_id = node.team_omega_id

            self.bracket_tree[match_id] = node
            round_1_matches.append(node)

        # Generate subsequent rounds placeholders
        prev_round_matches = round_1_matches
        for round_idx in range(2, total_rounds + 1):
            curr_round_matches = []
            for j in range(0, len(prev_round_matches), 2):
                next_id = f"R{round_idx}_M{j//2 + 1}_{uuid.uuid4().hex[:6]}"
                node = TournamentMatchNode(
                    match_id=next_id,
                    round_number=round_idx,
                    bracket_index=j // 2
                )
                prev_round_matches[j].next_match_id = next_id
                if j + 1 < len(prev_round_matches):
                    prev_round_matches[j + 1].next_match_id = next_id

                self.bracket_tree[next_id] = node
                curr_round_matches.append(node)
            prev_round_matches = curr_round_matches

        self.stage = TournamentStage.IN_PROGRESS
        return list(self.bracket_tree.values())

    def record_match_result(self, match_id: str, score_alpha: int, score_omega: int) -> Optional[str]:
        node = self.bracket_tree.get(match_id)
        if not node:
            return None

        node.score_alpha = score_alpha
        node.score_omega = score_omega
        node.completed_at = time.time()

        if score_alpha > score_omega:
            winner_id = node.team_alpha_id
            loser_id = node.team_omega_id
        else:
            winner_id = node.team_omega_id
            loser_id = node.team_alpha_id

        node.winner_team_id = winner_id

        if loser_id and loser_id in self.registered_teams:
            self.registered_teams[loser_id].is_eliminated = True

        # Advance to next match in bracket
        if node.next_match_id and node.next_match_id in self.bracket_tree:
            next_node = self.bracket_tree[node.next_match_id]
            if not next_node.team_alpha_id:
                next_node.team_alpha_id = winner_id
            else:
                next_node.team_omega_id = winner_id

        return winner_id

    def calculate_payout_distribution(self) -> Dict[str, Dict[str, int]]:
        # 1st Place: 50%, 2nd Place: 25%, 3rd-4th Place: 12.5% each
        payouts = {}
        # Find final match
        final_node = max(self.bracket_tree.values(), key=lambda n: n.round_number)
        champion_id = final_node.winner_team_id
        runner_up_id = final_node.team_omega_id if champion_id == final_node.team_alpha_id else final_node.team_alpha_id

        if champion_id:
            payouts[champion_id] = {
                "credits": int(self.prize_pool_credits * 0.50),
                "fracture_shards": int(self.prize_pool_shards * 0.50),
                "trophy": "CHAMPION_GOLD"
            }
        if runner_up_id:
            payouts[runner_up_id] = {
                "credits": int(self.prize_pool_credits * 0.25),
                "fracture_shards": int(self.prize_pool_shards * 0.25),
                "trophy": "RUNNER_UP_SILVER"
            }
        return payouts
