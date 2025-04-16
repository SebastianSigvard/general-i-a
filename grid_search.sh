#!/bin/zsh

EPISODES=50000
BATCH_SIZE=64
GAMMA_LIST=(0.94 0.96)
LR_LIST=(0.0004 0.0006)
HIDDEN_LAYERS="256,256,128"

mkdir -p logs

for GAMMA in $GAMMA_LIST; do
  for LR in $LR_LIST; do
    TAG="g${GAMMA}_lr${LR}_hl256x256x128"
    poetry run python src/train_qagent.py \
      --episodes $EPISODES \
      --batch-size $BATCH_SIZE \
      --gamma $GAMMA \
      --lr $LR \
      --hidden-layers $HIDDEN_LAYERS \
      --tag $TAG \
      > logs/train_${TAG}.log 2>&1 &
  done
done

wait
echo "All grid search jobs finished."