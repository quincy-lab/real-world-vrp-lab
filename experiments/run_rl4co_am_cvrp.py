"""Small RL4CO + Attention Model CVRP experiment.

Purpose
-------
Show the complete learning-based optimization loop in real code:

    state -> Attention Model policy -> actions -> reward -> REINFORCE update

This is deliberately a small training run so it can be inspected and executed
locally before we move to larger benchmark/pretrained-model experiments.
"""

import torch

from rl4co.envs import CVRPEnv
from rl4co.models import AttentionModelPolicy, REINFORCE
from rl4co.utils.trainer import RL4COTrainer


SEED = 42
NUM_CUSTOMERS = 20
EVAL_BATCH_SIZE = 16

# Keep the first run small. These are learning/demo settings, not paper settings.
TRAIN_EPOCHS = 1
TRAIN_BATCH_SIZE = 64
TRAIN_DATA_SIZE = 1_024
VAL_DATA_SIZE = 256
LEARNING_RATE = 1e-4


def evaluate(policy, env, td_eval):
    """Greedy rollout on a fixed batch so before/after are comparable."""
    policy.eval()
    with torch.inference_mode():
        out = policy(
            td_eval.clone(),
            env,
            phase="test",
            decode_type="greedy",
            return_actions=True,
        )

    rewards = out["reward"].detach().cpu()
    actions = out["actions"].detach().cpu()
    costs = -rewards
    return {
        "mean_cost": costs.mean().item(),
        "first_reward": rewards[0].item(),
        "first_cost": costs[0].item(),
        "first_actions": actions[0].tolist(),
    }


def print_state_action_reward(td_eval, eval_result):
    """Expose the three objects that matter most for understanding RL4CO."""
    print("\n=== State -> Action -> Reward ===")

    # STATE: TensorDict maintained by CVRPEnv.
    print("STATE")
    print(f"  TensorDict keys : {list(td_eval.keys())}")
    print(f"  depot shape     : {tuple(td_eval['locs'][..., 0, :].shape)}")
    print(f"  locations shape : {tuple(td_eval['locs'].shape)}")
    print(f"  demand shape    : {tuple(td_eval['demand'].shape)}")
    print(f"  feasible actions: {int(td_eval['action_mask'][0].sum().item())}")

    # ACTION: decoder output. 0 means depot; positive integers are customers.
    print("\nACTION")
    print(f"  first route action sequence: {eval_result['first_actions']}")

    # REWARD: RL4CO uses negative route length, so maximizing reward minimizes cost.
    print("\nREWARD")
    print(f"  reward = {eval_result['first_reward']:.4f}")
    print(f"  cost   = {eval_result['first_cost']:.4f} = -reward")


def main():
    torch.manual_seed(SEED)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 1) ENVIRONMENT: defines CVRP state, feasibility mask, transition and reward.
    env = CVRPEnv(generator_params={"num_loc": NUM_CUSTOMERS})

    # 2) POLICY: Kool-style encoder-decoder Attention Model.
    policy = AttentionModelPolicy(
        env_name=env.name,
        embed_dim=128,
        num_encoder_layers=3,
        num_heads=8,
    ).to(device)

    # 3) RL ALGORITHM: REINFORCE trains the policy from route rewards.
    model = REINFORCE(
        env,
        policy,
        baseline="rollout",
        batch_size=TRAIN_BATCH_SIZE,
        train_data_size=TRAIN_DATA_SIZE,
        val_data_size=VAL_DATA_SIZE,
        optimizer_kwargs={"lr": LEARNING_RATE},
    )

    # Fixed evaluation states: use exactly the same CVRP instances before/after training.
    td_eval = env.reset(batch_size=[EVAL_BATCH_SIZE]).to(device)

    before = evaluate(policy, env, td_eval)
    print("\n=== Before training ===")
    print(f"mean greedy cost : {before['mean_cost']:.4f}")
    print_state_action_reward(td_eval, before)

    # 4) LEARNING: policy parameters are updated from sampled routes and rewards.
    trainer = RL4COTrainer(
        max_epochs=TRAIN_EPOCHS,
        accelerator="gpu" if torch.cuda.is_available() else "cpu",
        devices=1,
        logger=False,
        enable_checkpointing=False,
    )
    trainer.fit(model)

    after = evaluate(model.policy.to(device), env, td_eval)
    print("\n=== After training ===")
    print(f"mean greedy cost : {after['mean_cost']:.4f}")
    print(f"before -> after  : {before['mean_cost']:.4f} -> {after['mean_cost']:.4f}")
    print(f"first actions    : {after['first_actions']}")
    print(f"first reward     : {after['first_reward']:.4f}")

    print("\nNote: one tiny epoch is a pipeline check, not a competitive benchmark.")


if __name__ == "__main__":
    main()
