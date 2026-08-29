import math
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import uuid

@dataclass
class PlayerRating:
    mu: float = 25.0       # Perceived skill mean
    sigma: float = 8.333   # Skill uncertainty
    matches_played: int = 0
    volatility: float = 0.06

    @property
    def conservative_rating(self) -> float:
        return max(0.0, self.mu - 3.0 * self.sigma)

@dataclass
class MatchmakingTicket:
    ticket_id: str
    profile_id: str
    username: str
    party_id: Optional[str]
    party_members: List[str]
    rating: PlayerRating
    region: str
    game_mode: str
    ping_map: Dict[str, float]
    created_at: float = field(default_factory=time.time)
    expanded_search_radius: float = 1.0

class TrueSkillMatchmakingEngine:
    BETA = 4.16666
    DRAW_PROBABILITY = 0.05
    INITIAL_MU = 25.0
    INITIAL_SIGMA = 8.333

    def __init__(self, region: str = "us-east"):
        self.region = region
        self.active_pool: List[MatchmakingTicket] = []
        self.max_lobby_size = 24
        self.min_lobby_size = 12

    def enqueue_ticket(self, ticket: MatchmakingTicket):
        self.active_pool.append(ticket)

    def dequeue_ticket(self, ticket_id: str) -> bool:
        initial_len = len(self.active_pool)
        self.active_pool = [t for t in self.active_pool if t.ticket_id != ticket_id]
        return len(self.active_pool) < initial_len

    def calculate_match_quality(self, team1: List[MatchmakingTicket], team2: List[MatchmakingTicket]) -> float:
        if not team1 or not team2:
            return 0.0

        mu_sum1 = sum(t.rating.mu for t in team1)
        sigma_sq_sum1 = sum(t.rating.sigma ** 2 for t in team1)

        mu_sum2 = sum(t.rating.mu for t in team2)
        sigma_sq_sum2 = sum(t.rating.sigma ** 2 for t in team2)

        total_players = len(team1) + len(team2)
        beta_sq = (self.BETA ** 2) * total_players

        denominator = math.sqrt(total_players * beta_sq + sigma_sq_sum1 + sigma_sq_sum2)
        if denominator == 0:
            return 0.0

        exponent = -((mu_sum1 - mu_sum2) ** 2) / (2 * denominator ** 2)
        quality = math.exp(exponent) * math.sqrt(beta_sq / (denominator ** 2))
        return min(1.0, max(0.0, quality))

    def evaluate_latency_penalty(self, team1: List[MatchmakingTicket], team2: List[MatchmakingTicket]) -> float:
        all_players = team1 + team2
        if not all_players:
            return 0.0

        pings = [t.ping_map.get(self.region, 50.0) for t in all_players]
        avg_ping = sum(pings) / len(pings)
        max_ping = max(pings)

        penalty = (avg_ping / 150.0) * 0.3 + (max_ping / 250.0) * 0.2
        return min(0.5, penalty)

    def find_best_match(self) -> Optional[Tuple[List[MatchmakingTicket], List[MatchmakingTicket]]]:
        if len(self.active_pool) < self.min_lobby_size:
            return None

        current_time = time.time()
        for ticket in self.active_pool:
            wait_time = current_time - ticket.created_at
            ticket.expanded_search_radius = 1.0 + (wait_time / 30.0) * 0.5

        sorted_pool = sorted(self.active_pool, key=lambda t: t.rating.conservative_rating)
        
        best_quality = 0.0
        best_pair = None

        chunk_size = self.max_lobby_size
        for i in range(0, len(sorted_pool) - chunk_size + 1):
            candidate_pool = sorted_pool[i : i + chunk_size]
            team1 = candidate_pool[0::2]
            team2 = candidate_pool[1::2]

            quality = self.calculate_match_quality(team1, team2)
            latency_pen = self.evaluate_latency_penalty(team1, team2)
            final_score = quality - latency_pen

            if final_score > 0.45 and final_score > best_quality:
                best_quality = final_score
                best_pair = (team1, team2)

        if best_pair:
            matched_ids = {t.ticket_id for t in best_pair[0] + best_pair[1]}
            self.active_pool = [t for t in self.active_pool if t.ticket_id not in matched_ids]
            return best_pair

        return None

    def update_ratings_post_match(
        self,
        winner_team: List[MatchmakingTicket],
        loser_team: List[MatchmakingTicket]
    ) -> Dict[str, PlayerRating]:
        updated = {}
        c = 1.0 / (2 * self.BETA)

        for winner in winner_team:
            v = 0.5
            w = 0.2
            new_mu = winner.rating.mu + (winner.rating.sigma ** 2 / c) * v
            new_sigma = winner.rating.sigma * math.sqrt(max(0.1, 1 - (winner.rating.sigma ** 2 / (c ** 2)) * w))
            updated[winner.profile_id] = PlayerRating(
                mu=new_mu,
                sigma=new_sigma,
                matches_played=winner.rating.matches_played + 1
            )

        for loser in loser_team:
            v = -0.5
            w = 0.2
            new_mu = loser.rating.mu - (loser.rating.sigma ** 2 / c) * v
            new_sigma = loser.rating.sigma * math.sqrt(max(0.1, 1 - (loser.rating.sigma ** 2 / (c ** 2)) * w))
            updated[loser.profile_id] = PlayerRating(
                mu=max(1.0, new_mu),
                sigma=new_sigma,
                matches_played=loser.rating.matches_played + 1
            )

        return updated
